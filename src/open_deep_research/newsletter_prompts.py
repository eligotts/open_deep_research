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
2. Every item MUST include the "block_type" field with one of: "research", "reconsideration"
3. Each item MUST have all required fields for its type:
   - Research: id, block_type, description, status, research_goal, desired_output, relevant_context
   - Reconsideration: id, block_type, description, status, reason, guiding_questions
4. The final item in the list MUST be a reconsideration block
5. Use empty strings for missing optional fields, do not omit them
</Output Format>
"""


# Query writer instructions
query_writer_instructions = """You are an expert research planner, tasked with generating targeted search queries for a specific research goal within a newsletter section.

<Research Task>
{research_goal}
</Research Task>

<Research Context>
Relevant Context: {relevant_context}
Desired Output Format: {desired_output}
Evaluation Criteria: {evaluation_criteria}
</Research Context>

<Task>
Generate {number_of_queries} search queries that will help accomplish this research goal. Your queries should be calibrated to the research needs and evaluation criteria.

Consider these factors when crafting queries:
1. Temporal Precision:
   - ALWAYS include specific date ranges or years when they appear in the research goal
   - For topics without explicit dates, focus on recent information (e.g., "2024", "last 2 years")
   - Use date-specific qualifiers (e.g., "before 2023", "since 2020") when temporal context matters
   - For historical topics, ensure proper time period coverage

2. Research Goal Alignment:
   - Queries should directly support the research goal
   - Consider the evaluation criteria as guidance for depth and focus
   - Align with the desired output format

3. Query Sophistication:
   - Use technical terminology appropriate to the topic
   - Combine key concepts to find specific intersections
   - Include temporal markers for time-sensitive information

4. Source Quality:
   - Target authoritative sources (academic, technical documentation, expert analysis)
   - Include terms that tend to appear in high-quality sources
   - Consider multiple types of sources based on the desired output

5. Context Integration:
   - Incorporate the relevant context provided
   - Consider how this research fits into the larger newsletter context

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
- Include appropriate date/time context
- Formatted for web search (no special operators unless specifically helpful)
</Output Format>"""

# Section writer instructions
section_writer_instructions = """You are an expert content writer, tasked with writing a section of a newsletter based on research findings.

<Research Goal>
{research_goal}
</Research Goal>

<Research Context>
Relevant Context: {relevant_context}
Desired Output Format: {desired_output}
Evaluation Criteria: {evaluation_criteria}
Current Output (if any): {current_output}
</Research Context>

<Source Material>
{source_str}
</Source Material>

<Task>
Write content that satisfies the research goal using the provided source material. Your writing should:

1. Content Requirements:
   - Directly address the research goal
   - Follow the desired output format exactly
   - Incorporate the relevant context
   - Build upon current output if it exists
   - Meet or exceed the evaluation criteria

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
Relevant Context: {relevant_context}
Desired Output Format: {desired_output}
Evaluation Criteria: {evaluation_criteria}
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
   - Does the content follow the desired output format?
   - Are all required elements present?
   - Is the structure appropriate?

3. Content Quality:
   - Is the information accurate and well-supported?
   - Are claims properly backed by sources?
   - Is the writing clear and professional?

4. Specific Criteria Compliance:
   - Does the content meet all evaluation criteria?
   - Is the relevant context properly incorporated?
   - Are all aspects fully developed?

If any criteria are not met, generate NO MORE THAN {number_of_queries} specific search queries to fill the most important gaps.
Prioritize the most critical missing information when generating follow-up queries.
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
- The evaluation criteria are not met

If the grade is "fail", you MUST provide no more than {number_of_queries} follow-up queries, focusing on the most important gaps.
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
