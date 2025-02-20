# Prompt for revising an existing execution plan
execution_plan_reviser_instructions = """You are an expert newsletter planner, tasked with either creating or revising an execution plan.

<Newsletter Topic>
{topic}
</Newsletter Topic>

<Newsletter Template>
{template}
</Newsletter Template>

<Current Execution Plan>
{current_plan}
</Current Execution Plan>

<Completed Items>
{completed_items}
</Completed Items>

<Pydantic Structures>
The execution plan must conform to these Pydantic models:

class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class EffortLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ExecutionItemBase(BaseModel):
    id: str                      # Unique identifier for this execution item
    description: str             # Short description of the task
    status: Status = Status.PENDING
    output: Optional[str] = ""   # Resulting output after execution
    dependencies: Optional[str] = ""  # What this item depends on

class ResearchItem(ExecutionItemBase):
    research_goal: str           # Specific research goal
    effort: EffortLevel = EffortLevel.MEDIUM
    important_context: Optional[str] = ""
    desired_output: Optional[str] = ""

class PlanReconsiderationItem(ExecutionItemBase):
    reason: str                  # Forward-looking explanation for reconsideration
    guiding_questions: Optional[List[str]] = []
    proposed_changes: Optional[str] = ""

class TemplateBuilderItem(ExecutionItemBase):
    template_goal: str           # Goal for constructing/updating newsletter template
    constraints: Optional[str] = ""
    current_structure: Optional[str] = ""
    notes: Optional[str] = ""

class ExecutionPlan(BaseModel):
    items: List[Union[ResearchItem, PlanReconsiderationItem, TemplateBuilderItem]]
</Pydantic Structures>

<Task>
Your task depends on the current state:

1. If this is the initial plan (current_plan is empty or only has the initial item):
   - Create a comprehensive execution plan for the newsletter
   - Start with research items for core topics
   - Include template builder items at strategic points
   - Add plan reconsideration items after major research phases

2. If this is a plan revision:
   - Review completed items and their outputs
   - Update or remove existing incomplete items
   - Add new items based on findings
   - Ensure dependencies are properly updated

For all items:
1. Research Items:
   - Set clear, specific research goals
   - Include relevant context and desired output format
   - Set appropriate effort levels
   - Make dependencies explicit

2. Template Builder Items:
   - Place after research that affects structure
   - Set clear template goals
   - Include formatting constraints
   - Reference relevant research outputs

3. Plan Reconsideration Items:
   - Place after pivotal research phases
   - Include specific guiding questions
   - Reference expected outputs

Item Naming Convention:
- Research: "research_[topic]_[number]"
- Template: "template_[purpose]_[number]"
- Reconsider: "reconsider_[phase]_[number]"

Dependencies Format:
"Depends on [specific item IDs or outputs]. Required because [clear explanation]."
</Task>

<Output Format>
You must return a valid ExecutionPlan object with this exact structure:

{{
    "items": [  # This 'items' field is required and must be a list
        {{
            "type": "research",  # Must be one of: "research", "reconsider", "template"
            "id": str,  # Follow naming convention
            "description": str,  # Clear, actionable description
            "status": "pending",  # Must be "pending" for new items
            "output": "",  # Empty string for new items
            "dependencies": str,  # Formatted dependency string
            "research_goal": str,  # Required for research type
            "effort": "low"|"medium"|"high",  # Required for research type
            "important_context": str,  # Optional for research type
            "desired_output": str  # Optional for research type
        }},
        {{
            "type": "reconsider",
            "id": str,
            "description": str,
            "status": "pending",
            "output": "",
            "dependencies": str,
            "reason": str,  # Required for reconsider type
            "guiding_questions": [str],  # Optional list of strings
            "proposed_changes": str  # Optional for reconsider type
        }},
        {{
            "type": "template",
            "id": str,
            "description": str,
            "status": "pending",
            "output": "",
            "dependencies": str,
            "template_goal": str,  # Required for template type
            "constraints": str,  # Optional for template type
            "notes": str  # Optional for template type
        }}
    ]
}}

Critical Requirements:
1. The output MUST have an "items" key containing a list
2. The list MUST NOT be empty
3. Each item MUST have all required fields for its type
4. Each item MUST include the "type" field
5. All string fields must be initialized (use empty string "" if no value)
6. Follow the exact structure shown above

Remember:
- The "items" field is mandatory and must be a list
- Each item must have a valid type and all required fields
- Initialize optional fields with empty strings rather than omitting them
</Output Format>"""


# Query writer instructions
query_writer_instructions = """You are an expert research planner, tasked with generating targeted search queries for a specific research goal within a newsletter section.

<Research Task>
{research_goal}
</Research Task>

<Research Context>
Important Background: {important_context}
Expected Output Format: {desired_output}
Effort Level: {effort}
Dependencies: {dependencies}
</Research Context>

<Task>
Generate {number_of_queries} search queries that will help accomplish this research goal. Your queries should be calibrated to the specified effort level:

- For "low" effort: Focus on high-level, authoritative overviews
- For "medium" effort: Balance between overview and specific details
- For "high" effort: Deep dive into technical details and multiple perspectives

Consider these factors when crafting queries:
1. Research Goal Alignment:
   - Queries should directly support the research goal
   - Account for any dependencies mentioned
   - Consider the desired output format

2. Query Sophistication:
   - Use technical terminology appropriate to the topic
   - Include recent year markers for timely information
   - Combine key concepts to find specific intersections

3. Source Quality:
   - Target authoritative sources (academic, technical documentation, expert analysis)
   - Include terms that tend to appear in high-quality sources
   - Consider multiple types of sources based on the desired output

4. Context Integration:
   - Incorporate relevant background information
   - Account for any dependencies on other research
   - Consider how this fits into the larger newsletter context

<Output Format>
The output must be a Queries object containing a list of SearchQuery objects:
{{
    "queries": [
        {{
            "search_query": str  # The actual search query string
        }}
    ]
}}

Each query should be:
- Self-contained (don't rely on context from other queries)
- Specific enough to return relevant results
- Formatted for web search (no special operators unless specifically helpful)
</Output Format>"""

# Section writer instructions
section_writer_instructions = """You are an expert content writer, tasked with writing a section of a newsletter based on research findings.

<Research Goal>
{research_goal}
</Research Goal>

<Research Context>
Important Background: {important_context}
Expected Output Format: {desired_output}
Dependencies: {dependencies}
Current Output (if any): {current_output}
</Research Context>

<Source Material>
{source_str}
</Source Material>

<Task>
Write content that satisfies the research goal using the provided source material. Your writing should:

1. Content Requirements:
   - Directly address the research goal
   - Follow the expected output format exactly
   - Incorporate relevant background information
   - Consider any dependencies mentioned
   - Build upon current output if it exists

2. Writing Guidelines:
   - Use clear, professional language
   - Support claims with evidence from sources
   - Maintain consistent technical depth
   - Structure content logically
   - Include relevant examples or case studies

3. Source Integration:
   - Cite sources appropriately
   - Synthesize information from multiple sources
   - Prioritize recent and authoritative sources
   - Resolve any conflicting information

Remember to:
- Stay focused on the research goal
- Follow the desired output format strictly
- Maintain appropriate technical depth
- Ensure all claims are supported by sources
</Task>

<Output Format>
Your output must be properly formatted content that matches the desired_output specification.
If no specific format is specified, use this default format:
1. Start with a bold key insight
2. Organize content into clear paragraphs
3. Use markdown formatting where appropriate
4. End with source citations
</Output Format>"""

# Instructions for section grading
section_grader_instructions = """You are an expert content reviewer, tasked with evaluating a section of a newsletter against its research goals.

<Research Goal>
{research_goal}
</Research Goal>

<Research Context>
Important Background: {important_context}
Expected Output Format: {desired_output}
Dependencies: {dependencies}
</Research Context>

<Section Content>
{section_content}
</Section Content>

<Task>
Evaluate whether the section meets all requirements and identify any gaps that need additional research.

Evaluation Criteria:
1. Goal Alignment:
   - Does the content directly address the research goal?
   - Are all key aspects of the goal covered?
   - Is the technical depth appropriate?

2. Format Compliance:
   - Does the content follow the expected output format?
   - Are all required elements present?
   - Is the structure appropriate?

3. Content Quality:
   - Is the information accurate and well-supported?
   - Are claims properly backed by sources?
   - Is the writing clear and professional?

4. Context Integration:
   - Is background information properly incorporated?
   - Are dependencies appropriately considered?
   - Is the content well-integrated with the broader context?

If any criteria are not met, generate specific search queries to fill the gaps.
</Task>

<Output Format>
{{
    "grade": "pass" | "fail",  # Whether the section meets all requirements
    "follow_up_queries": [     # Only if grade is "fail"
        {{
            "search_query": str  # Specific query to fill identified gaps
        }}
    ]
}}

The grade should be "fail" if ANY of the following are true:
- The research goal is not fully addressed
- The output format is not followed
- Key claims lack source support
- Critical information is missing
- Technical depth is inappropriate
</Output Format>"""

final_section_writer_instructions="""You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

<Section topic> 
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports: 
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point
</Task>

<Quality Checks>
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response
</Quality Checks>"""

# Prompt for updating the newsletter template based on new information
template_builder_instructions = """You are an expert newsletter architect, tasked with evolving the newsletter template based on new research and information.

<Newsletter Topic>
{topic}
</Newsletter Topic>

<Current Template>
{current_template}
</Current Template>

<Template Building Task>
{template_goal}
</Template Building Task>

<New Information>
{new_information}
</New Information>

<Task>
Update or create a new version of the newsletter template based on the template goal and new information. Your output must conform to the NewsletterTemplate structure with nested NewsletterSection objects.

Each NewsletterSection must have:
- name: Title of the section
- definition: Brief explanation of what it covers
- template: Guidelines for final output (optional)
- detail_level: One of ["idea", "partial", "complete"]
- dependencies: List of dependency notes
- children: List of subsections (if any)

The overall NewsletterTemplate must have:
- title: Newsletter title
- topic: Main focus
- summary: Brief overview
- sections: List of NewsletterSection objects
- desired_structure: Overall structure description
- additional_context: Extra guidance notes

Remember to:
1. Preserve existing sections when appropriate
2. Update detail_level based on available information
3. Maintain proper dependency relationships
4. Use the hierarchical structure effectively
5. Ensure all required fields are populated
6. Keep section definitions clear and focused

The template should evolve gradually - don't remove existing content unless explicitly required by the template goal.
</Task>

<Output Format>
The output must be a valid NewsletterTemplate object with this structure:
{{
    "title": str,
    "topic": str,
    "summary": str,
    "sections": [
        {{
            "name": str,
            "definition": str,
            "template": str | null,
            "output": str | null,
            "detail_level": "idea" | "partial" | "complete",
            "dependencies": [str],
            "children": [  # Recursive NewsletterSection structure
                {{
                    "name": str,
                    "definition": str,
                    ...
                }}
            ]
        }}
    ],
    "desired_structure": str | null,
    "additional_context": str | null
}}
</Output Format>"""
