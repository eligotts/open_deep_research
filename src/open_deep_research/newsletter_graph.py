from typing import Literal

from langchain_anthropic import ChatAnthropic 
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command

from src.open_deep_research.state import ReportStateInput, ReportStateOutput, Sections, ReportState, SectionState, SectionOutputState, Queries, Feedback
from src.open_deep_research.newsletter_state import NewsletterStateInput, NewsletterStateOutput, NewsletterState, ResearchBlockState, ResearchBlockOutputState, ExecutionPlan, PlanReconsiderationItem, Status, ResearchItem, TemplateBuilderItem, NewsletterTemplate, NewsletterSection
from src.open_deep_research.prompts import report_planner_query_writer_instructions, report_planner_instructions, query_writer_instructions, section_writer_instructions, final_section_writer_instructions, section_grader_instructions
from src.open_deep_research.newsletter_prompts import execution_plan_reviser_instructions, template_builder_instructions
from src.open_deep_research.configuration import Configuration
from src.open_deep_research.utils import tavily_search_async, deduplicate_and_format_sources, format_sections, perplexity_search

import json
# Set writer model
writer_model = ChatAnthropic(model=Configuration.writer_model, temperature=0) 
planner_model = ChatOpenAI(model=Configuration.planner_model)

# Nodes
def entry_worker(state: NewsletterState, config: RunnableConfig):
    """ Entry worker that creates the initial execution plan item """
    
    # Create the initial PlanReconsiderationItem with better description and reason
    initial_plan_reconsideration_item = PlanReconsiderationItem(
        id="initial_plan_creation",
        description="Create the initial execution plan for the newsletter generation process",
        status=Status.PENDING,
        output="",
        dependencies="No dependencies - this is the starting point",
        reason="Initial plan creation to establish the newsletter generation workflow",
        guiding_questions=[
            "What are the core research topics needed?",
            "When should template updates occur?",
            "What dependencies exist between sections?"
        ],
        proposed_changes=""
    )

    # Create the initial execution plan
    initial_execution_plan = ExecutionPlan(items=[initial_plan_reconsideration_item])

    return {"execution_plan": initial_execution_plan}


def execution_plan_builder(state: NewsletterState, config: RunnableConfig):
    """ Generate or revise the execution plan """

    # Get inputs
    topic = state["topic"]
    execution_plan = state.get("execution_plan")

    # Get the plan reconsideration item
    plan_reconsideration_item = execution_plan.items.pop(0)

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    report_structure = configurable.report_structure

    # Format the template structure
    if isinstance(report_structure, dict):
        template_str = json.dumps(report_structure, indent=2)
    elif isinstance(report_structure, NewsletterTemplate):
        template_str = report_structure.model_dump_json(indent=2)
    else:
        template_str = str(report_structure)

    # Format the current execution plan - handle empty plan case
    if not execution_plan.items:
        current_plan_str = "No existing items in plan"
    else:
        try:
            # Try to serialize the remaining items
            current_plan_str = json.dumps(
                {"items": [
                    {
                        "type": type(item).__name__.lower().replace("item", ""),
                        **item.model_dump()
                    } 
                    for item in execution_plan.items
                ]},
                indent=2
            )
        except Exception as e:
            print(f"Error serializing execution plan: {e}")
            current_plan_str = "Error formatting current plan"

    # Format completed items with clear structure
    completed_items = state.get("completed_items", [])
    if not completed_items:
        completed_items_str = "No completed items yet"
    else:
        completed_items_str = "\n\n".join([
            f"Item ID: {item.id}\n"
            f"Type: {type(item).__name__}\n"
            f"Description: {item.description}\n"
            f"Output: {item.output}"
            for item in completed_items
        ])

    # Generate system prompt
    system_instructions = execution_plan_reviser_instructions.format(
        topic=topic,
        template=template_str,
        current_plan=current_plan_str,
        completed_items=completed_items_str
    )

    # Generate/revise execution plan
    structured_llm = planner_model.with_structured_output(ExecutionPlan)
    execution_plan = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate or revise the execution plan based on the current state.")
    ])

    # Record the outcome in the reconsideration item's output
    plan_reconsideration_item.status = Status.COMPLETED
    plan_summary = "\n".join([
        f"- {item.id}: {item.description} ({type(item).__name__})"
        for item in execution_plan.items
    ])
    
    plan_reconsideration_item.output = (
        f"Plan {'created' if not completed_items else 'revised'}\n"
        f"Total items: {len(execution_plan.items)}\n"
        f"Items breakdown:\n{plan_summary}"
    )

    return {
        "execution_plan": execution_plan,
        "completed_items": plan_reconsideration_item
    }

def execution_orchestrator(state: NewsletterState, config: RunnableConfig):

    # Retreive the execution plan
    execution_plan = state["execution_plan"]

    # Get the current execution item
    current_execution_item = execution_plan.items[0]

    # If the current execution item is a research item, send it to the research worker
    if isinstance(current_execution_item, ResearchItem):

        # Here, we need to remove the item from the execution plan
        execution_plan.items.pop(0)
        return Command(goto=[
            Send("research_with_web_research", {"researchItem": current_execution_item})
        ])
    
    # If the current execution item is a plan reconsideration item, send it to the execution plan builder
    elif isinstance(current_execution_item, PlanReconsiderationItem):
        return Command(goto="execution_plan_builder")
    
    # If the current execution item is a template builder item, send it to the template builder
    else:
        return Command(goto="template_builder")
    
def template_builder(state: NewsletterState, config: RunnableConfig):
    """ Build or update the newsletter template """

    # Get the current execution plan and template builder item
    execution_plan = state["execution_plan"]
    template_builder_item = execution_plan.items.pop(0)

    # Get current state
    current_template = state.get("template", None)
    topic = state["topic"]
    
    # Format completed items for context
    new_information = "\n\n".join([
        f"Item {item.id}:\n"
        f"Type: {type(item).__name__}\n"
        f"Description: {item.description}\n"
        f"Output:\n{item.output}"
        for item in state.get("completed_items", [])
        if item.output
    ])

    # Generate system prompt
    system_instructions = template_builder_instructions.format(
        topic=topic,
        current_template=current_template.model_dump_json(indent=2) if current_template else "No template exists yet",
        template_goal=template_builder_item.template_goal,
        new_information=new_information if new_information else "No new information available"
    )

    # Generate new template
    structured_llm = writer_model.with_structured_output(NewsletterTemplate)
    new_template = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate or update the newsletter template based on the provided information.")
    ])

    # Record the changes in the template builder item's output
    template_builder_item.status = Status.COMPLETED
    template_builder_item.output = (
        f"Template updated:\n"
        f"Title: {new_template.title}\n"
        f"Sections: {len(new_template.sections)}\n"
        f"Changes: {template_builder_item.template_goal}"
    )

    return {
        "template": new_template,
        "completed_items": template_builder_item
    }

def generate_queries(state: ResearchBlockState, config: RunnableConfig):
    """ Generate search queries for a report section """

    # Get state 
    research_item = state["researchItem"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Generate queries 
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions with all ResearchItem fields
    system_instructions = query_writer_instructions.format(
        research_goal=research_item.research_goal,
        important_context=research_item.important_context,
        desired_output=research_item.desired_output,
        effort=research_item.effort.value,
        dependencies=research_item.dependencies,
        number_of_queries=number_of_queries
    )

    # Generate queries  
    queries = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries that will help accomplish this research goal.")
    ])

    return {"search_queries": queries.queries}

async def search_web(state: ResearchBlockState, config: RunnableConfig):
    """ Search the web for each query, then return a list of raw sources and a formatted string of sources."""
    
    # Get state 
    search_queries = state["search_queries"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Web search
    query_list = [query.search_query for query in search_queries]
    
    # Handle both cases for search_api:
    # 1. When selected in Studio UI -> returns a string (e.g. "tavily")
    # 2. When using default -> returns an Enum (e.g. SearchAPI.TAVILY)
    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    # Search the web
    if search_api == "tavily":
        search_results = await tavily_search_async(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=True)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=False)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    return {"source_str": source_str}

def write_section(state: ResearchBlockState, config: RunnableConfig) -> Command[Literal[END,"search_web"]]:
    """ Write a section of the newsletter based on research findings """

    # Get state 
    research_item = state["researchItem"]
    source_str = state["source_str"]

    # Format system instructions for writing
    system_instructions = section_writer_instructions.format(
        research_goal=research_item.research_goal,
        important_context=research_item.important_context or "No additional context provided",
        desired_output=research_item.desired_output or "No specific output format specified",
        dependencies=research_item.dependencies or "No dependencies",
        current_output=research_item.output or "No existing content",
        source_str=source_str
    )

    # Generate section content
    section_content = writer_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Write the section content based on the research findings.")
    ])
    
    # Store the generated content with metadata
    research_item.output = (
        f"Research Output:\n"
        f"Goal: {research_item.research_goal}\n"
        f"Content:\n{section_content.content}\n"
        f"Sources: Derived from {len(source_str.split('Source:')) - 1} sources"
    )

    # Format grading instructions
    grader_instructions = section_grader_instructions.format(
        research_goal=research_item.research_goal,
        important_context=research_item.important_context or "No additional context provided",
        desired_output=research_item.desired_output or "No specific output format specified",
        dependencies=research_item.dependencies or "No dependencies",
        section_content=section_content.content
    )

    # Grade the section
    structured_llm = writer_model.with_structured_output(Feedback)
    feedback = structured_llm.invoke([
        SystemMessage(content=grader_instructions),
        HumanMessage(content="Evaluate the section content against the research requirements.")
    ])

    if feedback.grade == "pass":
        research_item.status = Status.COMPLETED
        return Command(
            update={"completed_items": [research_item]},
            goto=END
        )
    else:
        return Command(
            update={
                "search_queries": feedback.follow_up_queries,
                "researchItem": research_item
            },
            goto="search_web"
        )
    

# Report section sub-graph -- 

# Add nodes 
research_worker = StateGraph(ResearchBlockState, output=ResearchBlockOutputState)
research_worker.add_node("generate_queries", generate_queries)
research_worker.add_node("search_web", search_web)
research_worker.add_node("write_section", write_section)

# Add edges
research_worker.add_edge(START, "generate_queries")
research_worker.add_edge("generate_queries", "search_web")
research_worker.add_edge("search_web", "write_section")

# Outer graph -- 

# Add nodes
builder = StateGraph(NewsletterState, input=NewsletterStateInput, output=NewsletterStateInput, config_schema=Configuration)
builder.add_node("entry_worker", entry_worker)
builder.add_node("execution_orchestrator", execution_orchestrator)
builder.add_node("execution_plan_builder", execution_plan_builder)
builder.add_node("research_with_web_research", research_worker.compile())
builder.add_node("template_builder", template_builder)

# Add edges
builder.add_edge(START, "entry_worker")
builder.add_edge("entry_worker", "execution_plan_builder")
builder.add_edge("execution_plan_builder", "execution_orchestrator")
builder.add_edge("research_with_web_research", "execution_orchestrator")
builder.add_edge("template_builder", "execution_orchestrator")
builder.add_edge("execution_orchestrator", END)

graph = builder.compile()