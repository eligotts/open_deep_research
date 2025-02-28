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

7. **Limit Scope to Content Creation**: Only include steps up to the completion of the newsletter content. Do not include any post-generation activities such as publishing, distribution, marketing, analytics, or feedback collection.

<Newsletter Metadata>
{newsletter_metadata}
</Newsletter Metadata>

Now create a comprehensive execution plan based on the provided newsletter metadata. The plan should enable autonomous generation of a high-quality newsletter that fully embodies the publication's established identity and purpose. Focus exclusively on the research, writing, and content refinement process ending with the final content ready for delivery.
"""

execution_block_creation_instructions = """You are an expert workflow planner tasked with advancing a modular newsletter production process. You have the following inputs:
	1.	Initial Execution Plan: A comprehensive, step-by-step plan outlining the creation of a newsletter.
	2.	Completed Execution Blocks: A list of research, template building, and reconsideration blocks that have already been executed (each with their outputs).
	3.	Recent Reconsideration Block: A block that was just completed, indicating a checkpoint where the current outputs were evaluated and new steps are needed.

Using these inputs, generate the next set of actionable execution blocks that will move the workflow forward. Important: Every block you generate must be immediately executable. In other words, do not create any execution block that depends on outputs which are not yet available. For instance, if a research block requires the outputs of previous research steps (e.g., for pairing analysis), do not generate it now. Instead, if additional dependent analysis is needed, stop at that point and end the output with a reconsideration block.

Structure your answer as a list of execution blocks. The list should include:
	•	Research Blocks: Each with a clear research goal, desired output, and any specific input parameters or evaluation criteria. Ensure that these blocks do not require any outputs from blocks that have not yet been executed.
	# •	Template Building Blocks: (if applicable) with clear goals for drafting content or outlines. These should only begin to be executed once significant research has taken place.
	•	A Final Reconsideration Block: The output list must conclude with a reconsideration block. This block will serve as a checkpoint to evaluate progress, integrate any dependency outputs, and propose potential adjustments to the plan for subsequent execution cycles. Importantly, this block is also where you should include guiding questions to determine if the research and drafting is complete and if it's time to write the final report. This final reconsideration would typically be preceded by a template builder item, as you would want to refine the draft before determining if it's ready for finalization.

Remember that the goal is to produce a sufficient draft, not a perfect one. Avoid excessive iterations between template building and reconsideration blocks. Once all major sections have adequate content and sufficient research has been completed, it's appropriate to mark the process as done and move to the final report generation.

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
      "description": "Description of reconsideration checkpoint including assessment of completion status",
      "status": "pending",
      "output": "",
      "reason": "Explanation for why reconsideration is needed or why completion assessment is appropriate at this point",
      "guiding_questions": ["Has enough research been completed to address all aspects of the newsletter?", "Does the current draft meet the quality and content requirements?", "Are there any gaps or sections needing additional development?", "Is the newsletter ready for final report generation?"],
      "proposed_changes": ""
    }}
  ],
  "done": false  // Set to true only when all research and drafting is complete and ready for final report generation
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
6. When creating a final reconsideration block to assess completion, include specific guiding questions about newsletter readiness and any necessary final improvements before generating the final report
7. Set the "done" field to true when sufficient research has been completed and each section has fleshed-out content ready to convert into a final report. Perfection is not required - only completeness and sufficiency. Avoid excessive iterations between template building and reconsideration. The newsletter is ready for final report generation when:
   - All required sections have substantive content addressing the main requirements
   - Sufficient research has been completed to support the content
   - The overall structure and tone match the newsletter requirements
   - Any remaining issues are minor refinements that can be addressed in final editing
ENSURE THE "done" FIELD IS PRESENT IN YOUR OUTPUT!
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
            "search_query": str  // The actual search query string
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
    "grade": "pass" | "fail",  // Whether the section meets all requirements
    "follow_up_queries": [     // Only if grade is "fail"
        {{
            "search_query": str  // Specific query to fill identified gaps
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
template_builder_instructions = """You are an expert newsletter architect, tasked with evolving the newsletter draft based on detailed metadata and new research information.

<Newsletter Metadata>
{newsletter_metadata}
</Newsletter Metadata>

<Current Draft>
{current_draft}
</Current Draft>

<Template Building Task>
{template_goal}
</Template Building Task>

<Constraints>
{constraints}
</Constraints>

<New Information>
{new_information}
</New Information>

<Additional Notes>
{notes}
</Aditional Notes>

<Task>
Your goal is to create or update a newsletter draft that fully embodies the newsletter's purpose, tone, and target audience as specified in the metadata. Integrate any new research findings to enrich the content while maintaining coherence and focus.

When creating or revising the draft:

1. Structure & Organization:
   - Craft a clear, logical structure with distinct sections that flow naturally
   - Ensure each section serves a specific purpose within the overall narrative
   - Maintain appropriate depth and breadth based on the newsletter's purpose and audience
   - Follow any structure type specified in the metadata

2. Content Development:
   - Incorporate new research findings thoughtfully, not simply appending them
   - Align content with the specified tone, writing style, and technical depth
   - Address the core topic and any relevant sub-themes identified in the metadata
   - Include recurring themes when appropriate for continuity across editions
   - Maintain focus on the newsletter's primary goal (inform, educate, persuade, etc.)

3. Quality & Refinement:
   - Ensure content is appropriate for the target audience's knowledge level
   - Follow the desired length guidelines (short, medium, long)
   - Refine language to match the specified writing style and tone
   - Identify areas that may need additional research or development
   - Provide constructive notes for further refinement

4. Integration & Evolution:
   - Build upon previous drafts when they exist, maintaining continuity
   - Honor all constraints while applying your expertise
   - Evolve the draft appropriately - early drafts should emphasize structure, later drafts should refine content
   - Identify potential gaps or opportunities for improvement

Remember that the goal is a cohesive, engaging newsletter that serves its specific purpose for its intended audience.
</Task>

<Output Format>
The output must be a valid ReportDraft object with this exact structure:
{{
    "draft_outline": str,  // High-level outline of the newsletter structure with intended focus for each section
    "sections": [          // List of sections representing individual parts of the newsletter
        {{
            "title": str,  // Title of the newsletter section
            "content": str // Draft content for this section
        }}
    ],
    "revision_notes": str  // Notes and suggestions for further refining the draft in subsequent iterations
}}

Guidelines for each field:
1. draft_outline:
   - Provide a clear, structured overview of the newsletter (250-350 words)
   - Include rationale for the structure and how it serves the newsletter's purpose
   - Highlight relationships between sections and overall narrative flow
   - Length: 200-400 words

2. sections:
   - Each section should have a clear, descriptive title
   - Content should be fully developed based on available information
   - Follow the style, tone, and depth specified in the metadata
   - Include transitions between sections for narrative coherence
   - Length: Appropriate to the section's purpose and overall newsletter length

3. revision_notes:
   - Identify specific areas that would benefit from additional research
   - Suggest refinements for tone, structure, or content focus
   - Note any missing elements that should be addressed in future iterations
   - Provide tactical suggestions for improving impact and engagement
   - Length: 150-300 words

The level of detail and completeness should evolve based on available information:
- Early drafts (minimal information): Focus on structure and placeholders
- Intermediate drafts: Develop content where research is available, identify gaps
- Advanced drafts: Refine language, improve flow, and enhance overall cohesion

Apply your expertise to create the most compelling and effective newsletter draft possible given the available information and constraints.
</Output Format>"""

# Define the research system prompt template
research_system_prompt_creation = """
# Research Agent Instructions

## Your Role
You are an expert research agent for newsletter content creation. Your goal is to conduct thorough research on a specific topic and produce high-quality, accurate content that will be used in a newsletter.

## Research Goal
{research_goal}

## Desired Output Format
{desired_output}

## Relevant Context
{relevant_context}

## Evaluation Criteria
{evaluation_criteria}

## Available Tools
You have access to the following tools to help with your research:
{tool_names}

## Research Process Guidelines:
1. Analyze the research goal and understand exactly what information is needed
2. Plan your research approach by breaking down the goal into smaller, manageable questions
3. Use the available tools to gather relevant, accurate, and up-to-date information
4. Verify information from multiple sources when possible
5. Organize your findings in a coherent manner
6. Ensure your research is thorough and addresses all aspects of the research goal
7. Filter out irrelevant or low-quality information
8. Synthesize the information into a cohesive narrative that meets the desired output format

## Important Instructions:
- Continue researching until you have gathered sufficient information to produce output that meets the evaluation criteria
- If initial research is insufficient, refine your approach and continue exploring
- Focus on depth and quality rather than breadth
- Critically evaluate all information for reliability, relevance, and accuracy
- If you encounter conflicting information, acknowledge it and explain your reasoning for choosing one perspective over another
- Ensure your output is comprehensive, accurate, and formatted according to the desired output guidelines

When you have completed your research, summarize your findings according to the desired output format. Your final output should fully satisfy the research goal and meet all evaluation criteria.
"""

# Build the system prompt for summarization
summary_system_prompt = """
You are tasked with summarizing research findings based on a conversation with a research agent.

## Research Goal
{research_goal}

## Desired Output Format
{desired_output}

## Evaluation Criteria
{evaluation_criteria}

## Research Findings
Below is the research conversation to summarize:
{conversation_context}

Create a comprehensive summary that fulfills the research goal and meets the desired output format.
Make sure your summary is:
1. Comprehensive and covers all key information
2. Well-structured according to the desired output format
3. Meets all evaluation criteria
4. Contains only factual information from the research
5. Cites specific sources where appropriate
"""
