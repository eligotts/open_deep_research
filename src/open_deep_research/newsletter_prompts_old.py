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


# Prompt for creating initial execution plan
initial_execution_plan_creation = """You are a professional newsletter production editor tasked with creating detailed execution plans for specialized newsletter creation. You will produce comprehensive, actionable plans that could be followed step-by-step to create high-quality newsletter content without additional guidance.

## Your Function

Create a detailed execution plan that outlines every concrete step needed to research, develop, and refine the newsletter content. Your plan must be extremely specific, focusing on exactly WHAT to do and HOW to do it, not WHY it should be done.

## Output Format and Structure

Title your plan:
```
# Execution Plan for "[Newsletter Title]: [Newsletter Topic]" ([Current Month/Quarter] Edition)
```

Organize your plan into functional phases focused on major content components, not abstract processes. Each phase should contain numbered, specific action steps:

```
## [Content Phase Name]
1. **[Specific Action Step]**
   - [Detailed instruction with exact methodology]
   - [Sub-step with specific parameters]
   - [Additional concrete action with expected output]

2. **[Next Action Step]**
   - [Detailed instructions...]
```

## Level of Detail Required

Your execution plan must be extremely detailed and actionable. For example:

- **Instead of**: "Research current events related to the newsletter topic"
- **Write**: "Identify 5-7 candidate current events using:
   - Major news sources (NYT, Washington Post, BBC, Al Jazeera) for the past 2-4 weeks
   - Academic journals including [specific journals] for scholarly perspectives
   - Industry reports from [specific organizations]
   - For each candidate event, document: key actors, timeline of developments, global/regional impact, and potential historical parallels"

- **Instead of**: "Write content for each section"
- **Write**: "Develop a 700-800 word detailed analysis of the historical event that includes:
   - Historical context and background (150-200 words)
   - Key actors and their motivations (150-200 words)
   - Critical developments and pivotal moments (200-250 words)
   - Immediate and long-term outcomes (150-200 words)
   - Use narrative techniques including character-driven storytelling and vivid scene descriptions"

## Essential Elements to Include

1. **Exact Research Methodologies**: Specify exactly which sources to consult, what data to extract, and how to organize findings.

2. **Precise Selection Criteria**: For any selection step, provide explicit criteria with weighting or priorities to guide decision-making.

3. **Specific Word Counts**: Assign target word counts for every content section and subsection.

4. **Detailed Content Requirements**: Outline exactly what information each section must contain down to the paragraph level.

5. **Concrete Evaluation Steps**: Include specific review criteria for assessing quality at each stage.

6. **Connection to Previous Editions**: Provide explicit instructions on how to reference and build upon past content.

7. **Strategic Flexibility Points**: When appropriate, identify specific decision points where research findings might necessitate course adjustments. Include brief guidance on how to recognize promising alternative paths and criteria for deciding when to pursue them.

## Tone and Approach

Write in a direct, instructional voice using active language. Your plan should read like detailed production notes from an expert editor to a skilled writing team. Assume domain expertise but provide specific technical guidance.

## Important Considerations

1. **Focus on Content Over Process**: Emphasize what content to create rather than abstract process steps.

2. **Be Exhaustive**: Leave no aspect of newsletter creation unaddressed.

3. **Maintain Consistent Detail**: Provide the same level of specificity across all phases and steps.

4. **Avoid Generalities**: Replace any general guidance with specific, actionable instructions.

5. **Use Domain-Specific Language**: Incorporate terminology and approaches specific to the newsletter's subject area.

6. **Balance Structure with Adaptability**: While providing detailed guidance, acknowledge places where findings might reveal more promising directions. Include brief criteria for recognizing when to adapt the approach based on intermediate discoveries.

<Newsletter Metadata>
{newsletter_metadata}
</Newsletter Metadata>

Now create a comprehensive execution plan based on the provided newsletter metadata. The plan should enable autonomous generation of a high-quality newsletter that fully embodies the publication's established identity and purpose.
"""

execution_block_creation_instructions = """You are an expert workflow planner tasked with advancing a modular newsletter production process. You have the following inputs:
	1.	Initial Execution Plan: A comprehensive, step-by-step plan outlining the creation of a newsletter.
	2.	Completed Execution Blocks: A list of research, template building, and reconsideration blocks that have already been executed (each with their outputs).
	3.	Recent Reconsideration Block: A block that was just completed, indicating a checkpoint where the current outputs were evaluated and new steps are needed.

Using these inputs, generate the next set of actionable execution blocks that will move the workflow forward. Important: Every block you generate must be immediately executable. In other words, do not create any execution block that depends on outputs which are not yet available. For instance, if a research block requires the outputs of previous research steps (e.g., for pairing analysis), do not generate it now. Instead, if additional dependent analysis is needed, stop at that point and end the output with a reconsideration block.

Structure your answer as a list of execution blocks. The list should include:
	•	Research Blocks: Each with a clear research goal, desired output, and any specific input parameters or evaluation criteria. Ensure that these blocks do not require any outputs from blocks that have not yet been executed.
	# •	Template Building Blocks: (if applicable) with clear goals for drafting content or outlines.
	•	A Final Reconsideration Block: The output list must conclude with a reconsideration block. This block will serve as a checkpoint to evaluate progress, integrate any dependency outputs, and propose potential adjustments to the plan for subsequent execution cycles.

Generate the new execution blocks in valid JSON format, ensuring that:
	•	Every block is immediately executable (i.e., does not depend on outputs that are not yet available).
	•	The final item in the list is always a reconsideration block.

<Initial Execution Plan>
{initial_execution_plan}
</Initial Execution Plan>

<Completed Items>
{completed_items}
</Completed Items>

<Recent Reconsideration Block>
{recent_reconsideration_block}
</Recent Reconsideration Block>

For reference, here is the newsletter metadata:
<Newsletter Metadata>
{newsletter_metadata}
</Newsletter Metadata>

<Output Format>
You must return a valid ExecutionPlan object with items in this exact structure:

{{
  "items": [
    // Research Blocks
    {{
      "id": "research_[topic]_[number]",
      "block_type": "research",
      "description": "Clear description of the research task",
      "status": "pending",
      "output": "",
      "research_goal": "Specific research objective",
      "desired_output": "Expected format or content of output",
      "relevant_context": "Any context needed for this research",
      "evaluation_criteria": "Criteria to assess research output"
    }},
    
    // Template Builder Blocks
    {{
      "id": "template_[purpose]_[number]",
      "block_type": "template_building",
      "description": "Clear description of template building task",
      "status": "pending",
      "output": "",
      "template_goal": "Goal for building/updating the template",
      "constraints": "Any formatting constraints",
      "notes": "Additional notes for template creation"
    }},
    
    // Reconsideration Block (always include as the final item)
    {{
      "id": "reconsider_[phase]_[number]",
      "block_type": "reconsideration",
      "description": "Description of reconsideration checkpoint",
      "status": "pending",
      "output": "",
      "reason": "Explanation for why reconsideration is needed",
      "guiding_questions": ["Question 1", "Question 2"],
      "proposed_changes": ""
    }}
  ]
}}

Important Requirements:
1. The response MUST be valid JSON with an "items" array
2. Every item MUST include the "block_type" field with one of: "research", "reconsideration", "template_building"
3. Each item MUST have all required fields for its type:
   - Research: id, block_type, description, status, research_goal, desired_output, relevant_context
   - Template Building: id, block_type, description, status, template_goal
   - Reconsideration: id, block_type, description, status, reason, guiding_questions
4. The final item in the list MUST be a reconsideration block
5. Use empty strings for missing optional fields, do not omit them
</Output Format>
"""