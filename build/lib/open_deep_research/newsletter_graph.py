from typing import Literal

from langchain_anthropic import ChatAnthropic 
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command

from langchain_community.tools import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langchain_community.tools.pubmed.tool import PubmedQueryRun
from langchain.agents import load_tools


from src.open_deep_research.newsletter_state import (
    NewsletterStateInput, NewsletterStateOutput, NewsletterState, 
    ResearchBlockState, ResearchBlockOutputState, ExecutionPlan, 
    ReconsiderationBlock, Status, ResearchBlock, TemplateBuilderItem, 
    ReportDraft, SchemaAdapter, openai_compatible, Queries, Feedback, BlockType
)
from src.open_deep_research.newsletter_prompts import template_builder_instructions, query_writer_instructions, section_writer_instructions, section_grader_instructions, initial_execution_plan_creation, execution_block_creation_instructions, research_system_prompt_creation, summary_system_prompt
from src.open_deep_research.configuration import Configuration
from src.open_deep_research.utils import tavily_search_async, deduplicate_and_format_sources, format_sections, perplexity_search
from src.open_deep_research.logger import NewsletterLogger


# Create a custom tool node that logs tool usage
class LoggingToolNode(ToolNode):
    """A wrapper around ToolNode that logs tool calls and responses"""
    
    def invoke(self, state, config=None):
        # Extract the tool call from the state
        tool_calls = []
        for message in state.get("messages", []):
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls.extend(message.tool_calls)
        
        # Call the original tool node
        result = super().invoke(state, config)
        
        # Log the tool responses
        logger = NewsletterLogger.get_current_logger()
        if logger and tool_calls:
            # Get the response messages
            response_messages = result.get("messages", [])
            
            # Match tool calls with responses
            for i, tool_call in enumerate(tool_calls):
                if i < len(response_messages):
                    response = response_messages[i].content if hasattr(response_messages[i], "content") else str(response_messages[i])
                    # Use the dedicated tool call logging method
                    logger.log_tool_call(
                        tool_name=tool_call.name,
                        tool_args=tool_call.args,
                        tool_response=response,
                        context=f"tool_execution_{tool_call.name}"
                    )
        
        return result

import json
# Set writer model
writer_model = ChatAnthropic(model=Configuration.writer_model, temperature=0) 
planner_model = ChatOpenAI(model=Configuration.planner_model)
# TOOLS
tavily_tool = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=False,
    # include_domains=[...],
    # exclude_domains=[...],
    # name="...",            # overwrite default tool name
    # description="...",     # overwrite default tool description
    # args_schema=...,       # overwrite default args_schema: BaseModel
)
tools = [tavily_tool, PubmedQueryRun()] + load_tools(
    ["arxiv"],
)
# Replace standard ToolNode with our logging version
tool_node = LoggingToolNode(tools)

model_with_tools = ChatAnthropic(model=Configuration.writer_model, temperature=0).bind_tools(tools)


# Nodes
def entry_worker(state: NewsletterState, config: RunnableConfig):
    """ Entry worker that creates the initial execution plan item """
    
    # Initialize a new logger for this run with hardcoded path
    logger = NewsletterLogger.initialize_new_logger()

    # Retrieve the newsletter metadata
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    newsletter_metadata = configurable.newsletter_metadata

    # Format the metadata into an organized string
    metadata_string = newsletter_metadata.model_dump_json(indent=4)

    # Format the initial execution plan creation prompt
    initial_execution_plan_creation_prompt = initial_execution_plan_creation.format(
        newsletter_metadata=metadata_string
    )

    # Generate the initial execution plan
    response = planner_model.invoke([
        SystemMessage(content=initial_execution_plan_creation_prompt),
        HumanMessage(content="Create the execution plan.")
    ])

    # Create the initial PlanReconsiderationItem with better description and reason
    initial_plan_reconsideration_item = ReconsiderationBlock(
        id="initial_plan_creation",
        block_type=BlockType.RECONSIDERATION,
        description="Create the initial execution plan for the newsletter generation process",
        status=Status.PENDING,
        output="",
        reason="This is the entry point for the workflow that will establish the full research and content generation plan for the newsletter",
        guiding_questions=[
            "What specific research blocks are needed to gather comprehensive information on the newsletter topic?",
            "How should the newsletter template be structured based on the newsletter metadata?",
            "What dependencies exist between different research components?",
            "At what points should plan reconsideration occur to evaluate and refine the approach?",
            "How should the research plan incorporate any recurring themes from past newsletters?",
            "What template building blocks will be needed and when should they be scheduled?"
        ],
        proposed_changes=""
    )

    # Create the initial execution plan
    initial_execution_plan = ExecutionPlan(items=[initial_plan_reconsideration_item], done=False)

    # Log the initial state
    logger.log_state_update(
        state_name="NewsletterState",
        state_data={"execution_plan": initial_execution_plan.model_dump(), "initial_execution_plan": response.content},
        node_name="entry_worker"
    )

    return {"execution_plan": initial_execution_plan, "initial_execution_plan": response.content, "newsletter_metadata": newsletter_metadata}

@openai_compatible
def generate_execution_plan(system_instructions: str) -> ExecutionPlan:
    """Helper function to generate execution plan using OpenAI"""
    response = planner_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate or revise the execution plan based on the current state.")
    ])
    
    # Get the current logger instance
    logger = NewsletterLogger.get_current_logger()
    if logger:
        # Log the LLM interaction
        logger.log_llm_interaction(
            prompt=system_instructions,
            response=response.content,
            context="execution_plan_builder"
        )
    
    # Parse the content from the AIMessage into our ExecutionPlan model
    return ExecutionPlan.model_validate_json(response.content)

def execution_plan_builder(state: NewsletterState, config: RunnableConfig):
    """ Generate or revise the execution plan """

    # Get inputs
    newsletter_metadata = state["newsletter_metadata"]
    execution_plan = state.get("execution_plan")
    initial_plan_text = state.get("initial_execution_plan", "")

    # Get the plan reconsideration item that triggered this update
    plan_reconsideration_item = execution_plan.items.pop(0)
    
    # Get the current logger instance
    logger = NewsletterLogger.get_current_logger()

    # Format the recent reconsideration block for prompt
    recent_block_str = (
        f"ID: {plan_reconsideration_item.id}\n"
        f"Description: {plan_reconsideration_item.description}\n"
        f"Reason: {plan_reconsideration_item.reason}\n"
        f"Guiding Questions:\n" + 
        "\n".join([f"- {question}" for question in plan_reconsideration_item.guiding_questions]) + "\n"
        f"Proposed Changes: {plan_reconsideration_item.proposed_changes if plan_reconsideration_item.proposed_changes else 'None yet - awaiting execution'}"
    )

    # Format completed items with structure appropriate for execution items
    completed_items = state.get("completed_items", [])
    if not completed_items:
        completed_items_str = "No completed items yet"
    else:
        # Create detailed formatted string for completed items
        completed_items_parts = []
        for item in completed_items:
            item_type = type(item).__name__
            
            # Basic info for all types
            item_info = [
                f"ID: {item.id}",
                f"Type: {item_type}",
                f"Block Type: {item.block_type.value}",
                f"Description: {item.description}",
                f"Status: {item.status.value}"
            ]
            
            # Add type-specific fields
            if isinstance(item, ResearchBlock):
                item_info.extend([
                    f"Research Goal: {item.research_goal}",
                    f"Desired Output: {item.desired_output}",
                    f"Relevant Context: {item.relevant_context}",
                    f"Evaluation Criteria: {item.evaluation_criteria if item.evaluation_criteria else 'None'}"
                ])
            elif isinstance(item, ReconsiderationBlock):
                item_info.extend([
                    f"Reason: {item.reason}",
                    f"Guiding Questions: {', '.join(item.guiding_questions) if item.guiding_questions else 'None'}",
                    f"Proposed Changes: {item.proposed_changes if item.proposed_changes else 'None'}"
                ])
            elif isinstance(item, TemplateBuilderItem):
                item_info.extend([
                    f"Template Goal: {item.template_goal}",
                    f"Constraints: {item.constraints if item.constraints else 'None'}",
                    f"Notes: {item.notes if item.notes else 'None'}"
                ])
            
            # Add output for all types
            item_info.append(f"Output: {item.output if item.output else 'No output generated'}")
            
            # Join item info with line breaks and add to parts
            completed_items_parts.append("\n".join(item_info))
        
        # Join all items with clear separation
        completed_items_str = "\n\n---\n\n".join(completed_items_parts)

    # Generate system prompt using the execution_block_creation_instructions
    system_instructions = execution_block_creation_instructions.format(
        initial_execution_plan=initial_plan_text,
        completed_items=completed_items_str,
        recent_reconsideration_block=recent_block_str,
        newsletter_metadata=newsletter_metadata.model_dump_json(indent=4)
    )

    # Generate/revise execution plan using our OpenAI-compatible helper
    execution_plan = generate_execution_plan(system_instructions)

    # Record the outcome in the reconsideration item's output
    plan_reconsideration_item.status = Status.COMPLETED
    plan_summary = "\n".join([
        f"- {item.id}: {item.description} ({item.block_type.value})"
        for item in execution_plan.items
    ])
    
    plan_reconsideration_item.output = (
        f"Plan {'created' if not completed_items else 'revised'}\n"
        f"Total items: {len(execution_plan.items)}\n"
        f"Items breakdown:\n{plan_summary}"
    )

    # Log the execution item update
    if logger:
        logger.log_execution_item(
            item_type="ReconsiderationBlock",
            item_id=plan_reconsideration_item.id,
            description=plan_reconsideration_item.description,
            status=plan_reconsideration_item.status.value,
            output=plan_reconsideration_item.output
        )

    return {
        "execution_plan": execution_plan,
        "completed_items": [plan_reconsideration_item]
    }

def execution_orchestrator(state: NewsletterState, config: RunnableConfig):

    # Retreive the execution plan
    execution_plan = state["execution_plan"]

    # Get the current execution item
    current_execution_item = execution_plan.items[0]

    # If the current execution item is a research item, send it to the research worker
    if isinstance(current_execution_item, ResearchBlock):

        # Here, we need to remove the item from the execution plan
        execution_plan.items.pop(0)
        return Command(goto=[
            Send("research_with_web_research", {"researchItem": current_execution_item})
        ],
        update={"execution_plan": execution_plan}
        )
    
    # If the current execution item is a plan reconsideration item, send it to the execution plan builder
    elif isinstance(current_execution_item, ReconsiderationBlock):
        return Command(goto="execution_plan_builder")
    
    # If the current execution item is a template builder item, send it to the template builder
    else:
        return Command(goto="template_builder")
    
def template_builder(state: NewsletterState, config: RunnableConfig):
    """ Build or update the newsletter template """

    # Get the current execution plan and template builder item
    execution_plan = state["execution_plan"]
    template_builder_item = execution_plan.items.pop(0)


    # Get the metadata
    newsletter_metadata = state["newsletter_metadata"]

    # Get the current report draft if it exists
    current_draft = state.get("draft", None)

    # get the topic, title, target audience, newsletter_goal, desired_tone, content_focus, content_type
    # structure_type, desired_length, preferred_writing_style, template, and format into a clean string
    metadata_dict = {
        "Topic": newsletter_metadata.topic,
        "Title": newsletter_metadata.title if newsletter_metadata.title else "Not specified",
        "Target Audience": newsletter_metadata.target_audience,
        "Newsletter Goal": newsletter_metadata.newsletter_goal,
        "Desired Tone": newsletter_metadata.desired_tone,
        "Content Focus": newsletter_metadata.content_focus if newsletter_metadata.content_focus else "Not specified",
        "Content Type": newsletter_metadata.content_type if newsletter_metadata.content_type else "Not specified",
        "Structure Type": newsletter_metadata.structure_type if newsletter_metadata.structure_type else "Not specified",
        "Desired Length": newsletter_metadata.desired_length.value if newsletter_metadata.desired_length else "Not specified",
        "Preferred Writing Style": newsletter_metadata.preferred_writing_style if newsletter_metadata.preferred_writing_style else "Not specified",
        "Template": newsletter_metadata.template if newsletter_metadata.template else "Not specified"
    }
    
    # Convert to formatted string
    formatted_metadata = "\n".join([f"{key}: {value}" for key, value in metadata_dict.items()])
    
    # Get recurring themes if they exist
    if newsletter_metadata.recurring_themes:
        formatted_metadata += "\nRecurring Themes: " + ", ".join(newsletter_metadata.recurring_themes)

    # Get any completed items that might contain information relevant to the template
    completed_items = state.get("completed_items", [])
    new_information = ""
    
    if completed_items:
        # Format relevant completed items for template context
        research_outputs = []
        for item in completed_items:
            if isinstance(item, ResearchBlock) and item.status == Status.COMPLETED:
                research_outputs.append(f"Research: {item.id}\nGoal: {item.research_goal}\nOutput: {item.output}")
        
        if research_outputs:
            new_information = "Research Findings:\n" + "\n\n".join(research_outputs)

    # Get the current logger instance
    logger = NewsletterLogger.get_current_logger()

    try:
        # Generate system prompt
        system_instructions = template_builder_instructions.format(
            newsletter_metadata=formatted_metadata,
            current_draft=current_draft.model_dump_json(indent=2) if isinstance(current_draft, ReportDraft) else "No draft exists yet",
            template_goal=template_builder_item.template_goal,
            constraints=template_builder_item.constraints if template_builder_item.constraints else "No specific constraints",
            new_information=new_information if new_information else "No new information available",
            notes=template_builder_item.notes if template_builder_item.notes else "No additional notes"
        )

        # Generate new template using our OpenAI-compatible helper
        new_draft = generate_report_draft(system_instructions)

        # Log the template update
        if logger:
            logger.log_template_update(
                template=new_draft.model_dump(),
                reason=template_builder_item.template_goal,
                node_name="template_builder"
            )

        # set the new template to be the output of the template_builder_item
        template_builder_item.output = new_draft.model_dump_json(indent=4)
        
        # set it to complete
        template_builder_item.status = Status.COMPLETED

        return {
            "draft": new_draft,
            "completed_items": [template_builder_item]
        }
    except Exception as e:
        # Log any errors during template building
        if logger:
            logger.log_error(e, f"Error building template for {template_builder_item.id}")
        raise

@openai_compatible
def generate_report_draft(system_instructions: str) -> ReportDraft:
    """Helper function to generate report draft using OpenAI"""
    response = planner_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate or update the report draft based on the provided information.")
    ])
    
    # Get the current logger instance
    logger = NewsletterLogger.get_current_logger()
    if logger:
        # Log the LLM interaction
        logger.log_llm_interaction(
            prompt=system_instructions,
            response=response.content,
            context="template_builder"
        )
    
    # Parse the content from the AIMessage into our NewsletterTemplate model
    return ReportDraft.model_validate_json(response.content)

def generate_queries(state: ResearchBlockState, config: RunnableConfig):
    """ Generate search queries for a report section """

    # Get state 
    research_item = state["researchItem"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Format system instructions with all ResearchItem fields
    system_instructions = query_writer_instructions.format(
        research_goal=research_item.research_goal,
        relevant_context=research_item.relevant_context,
        desired_output=research_item.desired_output,
        evaluation_criteria=research_item.evaluation_criteria or "No specific evaluation criteria provided",
        number_of_queries=number_of_queries
    )

    # Generate queries using our OpenAI-compatible helper
    queries = generate_search_queries(system_instructions)

    return {"search_queries": queries.queries}

@openai_compatible
def generate_search_queries(system_instructions: str) -> Queries:
    """Helper function to generate search queries using OpenAI"""
    response = planner_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries that will help accomplish this research goal.")
    ])
    
    # Get the current logger instance
    logger = NewsletterLogger.get_current_logger()
    if logger:
        # Log the LLM interaction
        logger.log_llm_interaction(
            prompt=system_instructions,
            response=response.content,
            context="generate_queries"
        )
    
    # Parse the content from the AIMessage into our Queries model
    return Queries.model_validate_json(response.content)

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

    try:
        # Search the web
        if search_api == "tavily":
            search_results = await tavily_search_async(query_list)
            source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=True)
        elif search_api == "perplexity":
            search_results = perplexity_search(query_list)
            source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=False)
        else:
            raise ValueError(f"Unsupported search API: {configurable.search_api}")

        # Log the web search
        logger = NewsletterLogger.get_current_logger()
        if logger:
            logger.log_web_search(
                queries=query_list,
                results=search_results,
                search_api=search_api
            )

        return {"source_str": source_str}
    except Exception as e:
        # Log any errors during web search
        logger = NewsletterLogger.get_current_logger()
        if logger:
            logger.log_error(e, f"Error during web search with {search_api}")
        raise

def write_section(state: ResearchBlockState, config: RunnableConfig) -> Command[Literal[END,"search_web"]]:
    """ Write a section of the newsletter based on research findings """

    # Get state 
    research_item = state["researchItem"]
    source_str = state["source_str"]

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    # Format system instructions for writing
    system_instructions = section_writer_instructions.format(
        research_goal=research_item.research_goal,
        relevant_context=research_item.relevant_context or "No additional context provided",
        desired_output=research_item.desired_output or "No specific output format specified",
        evaluation_criteria=research_item.evaluation_criteria or "No specific evaluation criteria provided",
        current_output=research_item.output or "No existing content",
        source_str=source_str
    )

    try:
        # Generate section content
        section_content = writer_model.invoke([
            SystemMessage(content=system_instructions),
            HumanMessage(content="Write the section content based on the research findings.")
        ])

        # Log the LLM interaction
        logger = NewsletterLogger.get_current_logger()
        if logger:
            logger.log_llm_interaction(
                prompt=system_instructions,
                response=section_content.content,
                context=f"Writing section for {research_item.id}"
            )
        
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
            relevant_context=research_item.relevant_context or "No additional context provided",
            desired_output=research_item.desired_output or "No specific output format specified",
            evaluation_criteria=research_item.evaluation_criteria or "No specific evaluation criteria provided",
            section_content=section_content.content,
            number_of_queries=number_of_queries
        )

        # Grade the section
        structured_llm = writer_model.with_structured_output(Feedback)
        feedback = structured_llm.invoke([
            SystemMessage(content=grader_instructions),
            HumanMessage(content="Evaluate the section content against the research requirements.")
        ])

        # Log the grading interaction
        logger = NewsletterLogger.get_current_logger()
        if logger:
            logger.log_llm_interaction(
                prompt=grader_instructions,
                response=feedback.model_dump(),
                context=f"Grading section for {research_item.id}"
            )

        if feedback.grade == "pass":
            research_item.status = Status.COMPLETED
            
            # Log the completed research item
            logger = NewsletterLogger.get_current_logger()
            if logger:
                logger.log_execution_item(
                    item_type="ResearchItem",
                    item_id=research_item.id,
                    description=research_item.description,
                    status=research_item.status.value,
                    output=research_item.output
                )
            
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
    except Exception as e:
        # Log any errors during section writing
        logger = NewsletterLogger.get_current_logger()
        if logger:
            logger.log_error(e, f"Error writing section for {research_item.id}")
        raise

def build_research_system_prompt(state: ResearchBlockState):

    # retreive the research block
    research_item = state["researchItem"]

    # Get the names of available tools as a comma-separated string
    tool_names = ", ".join([tool.name for tool in tools])
    
    # build the system prompt
    research_system_prompt = research_system_prompt_creation.format(
        research_goal=research_item.research_goal,
        desired_output=research_item.desired_output,
        relevant_context=research_item.relevant_context or "No additional context provided",
        evaluation_criteria=research_item.evaluation_criteria or "No specific evaluation criteria provided",
        tool_names=tool_names
    )
    
    # Log the system prompt creation
    logger = NewsletterLogger.get_current_logger()
    if logger:
        # Log the system prompt
        logger.log_llm_interaction(
            prompt=research_system_prompt,
            response="System prompt created",
            context=f"Building research system prompt for {research_item.id}"
        )
        
        # Also log the start of a new research task with more details
        logger.log_execution_item(
            item_type="ResearchBlock",
            item_id=research_item.id,
            description=research_item.description,
            status="in_progress",
            output=f"Starting research task with goal: {research_item.research_goal}\nDesired output: {research_item.desired_output}"
        )

    # Return the system prompt as a message to be sent to the model
    return {"messages": [SystemMessage(content=research_system_prompt), HumanMessage(content="Please conduct the research.")]}


def should_continue(state: ResearchBlockState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


def call_model(state: ResearchBlockState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    
    # Log the model interaction and any tool calls
    logger = NewsletterLogger.get_current_logger()
    if logger:
        # Get the last human message for context
        last_human_message = next((msg.content for msg in reversed(messages) 
                                if isinstance(msg, HumanMessage)), "No human message")
        
        # Log the basic interaction
        logger.log_llm_interaction(
            prompt=last_human_message,
            response=response.content,
            context="agent_with_tools"
        )
        
        # Log any tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                # Use the dedicated tool call logging method
                logger.log_tool_call(
                    tool_name=tool_call.name,
                    tool_args=tool_call.args,
                    tool_response="Pending tool response",
                    context=f"tool_call_request_{tool_call.name}"
                )
    
    return {"messages": [response]}


def end_node(state: ResearchBlockState):
    # retreive the research block
    research_item = state["researchItem"]
    messages = state["messages"]
    
    # Extract relevant information from messages for summarization
    conversation_context = "\n\n".join([
        f"{msg.type}: {msg.content}" 
        for msg in messages 
        if hasattr(msg, "content") and msg.content
    ])
    
    # Build the system prompt for summarization
    summary_system_prompt_final = summary_system_prompt.format(
        research_goal=research_item.research_goal,
        desired_output=research_item.desired_output,
        evaluation_criteria=research_item.evaluation_criteria or "No specific evaluation criteria provided",
        conversation_context=conversation_context
    )

    # Generate the summary
    summary = writer_model.invoke([
        SystemMessage(content=summary_system_prompt_final),
        HumanMessage(content="Please summarize the research findings.")
    ])

    # Log the summary generation
    logger = NewsletterLogger.get_current_logger()
    if logger:
        logger.log_llm_interaction(
            prompt=summary_system_prompt_final,
            response=summary.content,
            context=f"Generating summary for {research_item.id}"
        )

    # Update the research item with the summary and mark as completed
    research_item.output = summary.content
    research_item.status = Status.COMPLETED
    
    # Log the completed research item
    if logger:
        logger.log_execution_item(
            item_type="ResearchItem",
            item_id=research_item.id,
            description=research_item.description,
            status=research_item.status.value,
            output=research_item.output
        )

    # Return the completed research item
    return Command(
        update={"completed_items": [research_item]},
        goto=END
    )

def check_done(state: NewsletterState):

    if state["execution_plan"].done:
        return END
    return "execution_orchestrator"
# Report section sub-graph -- 

# Add nodes 
research_worker = StateGraph(ResearchBlockState, output=ResearchBlockOutputState)
research_worker.add_node("generate_context_prompt", build_research_system_prompt)
research_worker.add_node("agent", call_model)
research_worker.add_node("tools", tool_node)
research_worker.add_node("end", end_node)

# Add edges
research_worker.add_edge(START, "generate_context_prompt")
research_worker.add_edge("generate_context_prompt", "agent")
research_worker.add_conditional_edges("agent", should_continue, ["tools", "end"])
research_worker.add_edge("tools", "agent")

# # Add nodes 
# research_worker = StateGraph(ResearchBlockState, output=ResearchBlockOutputState)
# research_worker.add_node("generate_queries", generate_queries)
# research_worker.add_node("search_web", search_web)
# research_worker.add_node("write_section", write_section)

# # Add edges
# research_worker.add_edge(START, "generate_queries")
# research_worker.add_edge("generate_queries", "search_web")
# research_worker.add_edge("search_web", "write_section")

# Outer graph -- 

# Add nodes
# builder = StateGraph(NewsletterState, input=NewsletterStateInput, output=NewsletterStateInput, config_schema=Configuration)
builder = StateGraph(NewsletterState, output=NewsletterStateInput, config_schema=Configuration)
builder.add_node("entry_worker", entry_worker)
builder.add_node("execution_orchestrator", execution_orchestrator)
builder.add_node("execution_plan_builder", execution_plan_builder)
builder.add_node("research_with_web_research", research_worker.compile())
builder.add_node("template_builder", template_builder)

# Add edges
builder.add_edge(START, "entry_worker")
builder.add_edge("entry_worker", "execution_plan_builder")
# builder.add_edge("execution_plan_builder", "execution_orchestrator")
builder.add_conditional_edges("execution_plan_builder", check_done, ["execution_orchestrator", END])
builder.add_edge("research_with_web_research", "execution_orchestrator")
builder.add_edge("template_builder", "execution_orchestrator")
# builder.add_edge("execution_orchestrator", END)

graph = builder.compile()