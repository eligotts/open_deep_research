from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# Enumerations for common options
class FrequencyEnum(str, Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BI_WEEKLY = "Bi-Weekly"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"

class LengthEnum(str, Enum):
    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"

# Model representing a past newsletter edition
class PastNewsletter(BaseModel):
    newsletter_id: str = Field(
        ..., 
        description="Unique identifier for the newsletter edition, typically following a consistent format (e.g., 'HELP-001')"
    )
    publication_date: datetime = Field(
        ..., 
        description="Date and time when the newsletter was published or generated, used for tracking chronology and frequency adherence"
    )
    title: str = Field(
        ..., 
        description="Title or subject line of the newsletter edition, capturing the main focus or theme"
    )
    summary: str = Field(
        ..., 
        description="Concise summary of the newsletter content, highlighting key points and themes covered"
    )

# Main model for newsletter metadata with state retention for past newsletters
class NewsletterMetadata(BaseModel):
    # I. Newsletter Identity & Purpose (Core Defining Metadata)
    # I. Newsletter Identity & Purpose (Core Defining Metadata)
    topic: str = Field(
        ..., 
        description="Primary theme or subject matter of the newsletter, defining its overall focus and scope"
    )
    title: Optional[str] = Field(
        None, 
        description="Official title of the newsletter series, distinct from individual edition titles"
    )
    target_audience: str = Field(
        ..., 
        description="Detailed description of the intended readership, including demographics, interests, and knowledge level"
    )
    newsletter_goal: str = Field(
        ..., 
        description="The primary objective of the newsletter (e.g., to inform, educate, entertain, inspire action)"
    )
    desired_tone: str = Field(
        ..., 
        description="The stylistic tone/voice for the newsletter (e.g., formal, conversational, technical, inspirational)"
    )

    # II. Content & Style Preferences (Guiding Content Generation)
    # II. Content & Style Preferences (Guiding Content Generation)
    content_focus: Optional[str] = Field(
        None, 
        description="Specific sub-themes, angles, or aspects within the broader topic to emphasize"
    )
    content_type: Optional[str] = Field(
        None, 
        description="The primary content approach (e.g., case study, tutorial, analysis, interview)"
    )
    structure_type: Optional[str] = Field(
        None, 
        description="The overall structure format for the newsletter (e.g., standard analysis, comparative, diary format)"
    )
    desired_length: Optional[LengthEnum] = Field(
        None, 
        description="Target length category for the newsletter (Short, Medium, or Long)"
    )
    preferred_writing_style: Optional[str] = Field(
        None, 
        description="Detailed description of the writing style, potentially with examples (e.g., 'Concise and journalistic, similar to The Hustle')"
    )
    template: Optional[str] = Field(
        None, 
        description="String template or structured format for the newsletter, potentially with placeholders for dynamic content"
    )
    recurring_themes: Optional[List[str]] = Field(
        None, 
        description="Themes or topics that should appear regularly across editions for consistency"
    )

    # III. Workflow & Generation Settings (Platform-Specific Metadata)
    generation_frequency: FrequencyEnum = Field(
        ..., 
        description="How often the newsletter is generated (Daily, Weekly, Bi-Weekly, Monthly, Quarterly)"
    )
    continuity: Optional[str] = Field(
        None, 
        description="How newsletters should connect across editions, including thematic links or narrative progression"
    )

    # State retention: a list of past newsletters for maintaining continuity and avoiding repetition
    past_newsletters: List[PastNewsletter] = Field(
        default_factory=list,
        description="Archive of past newsletter editions for maintaining continuity, tracking themes, and avoiding repetition"
    )

topic1 = """
Historical Echoes: “Lessons from the Past”

Frequency: Monthly
Structure: Comparative Analysis
Content: Each report connects a major recent event to a historical parallel, ensuring variety across topics. If requested, a “Lessons Revisited” section revisits past comparisons to assess how accurate or relevant they still are.
Value: Provides historical context for current issues while ensuring thematic continuity over time.
"""

plan1 = """
Below is the updated research plan tailored to a “Lessons from the Past” newsletter that, in each edition, focuses on one current event paired with one historical event—and builds a narrative continuity from one issue to the next.

Research Plan: Historical Echoes – “Lessons from the Past”

1. Overview & Objectives
	•	Newsletter Topic:
“Lessons from the Past”
	•	Frequency & Structure:
Monthly, structured as a Comparative Analysis
	•	Content Focus:
	•	Primary Focus: Each edition examines one significant current event and connects it to one relevant historical event.
	•	Continuity: Over successive editions, these event pairings form a connected narrative, highlighting evolving themes and recurring lessons.
	•	Supplementary Section: Optionally, include a “Lessons Revisited” segment that reviews how earlier comparisons hold up over time.
	•	Value Proposition:
Provides readers with a deep, focused analysis of a single current event in the context of history, while gradually building a broader narrative across issues.
	•	Key Outcomes:
	•	A clear candidate current event for the edition.
	•	A well-chosen historical event that offers meaningful context or contrast.
	•	A roadmap for integrating each pairing into an ongoing storyline across newsletters.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata
	•	User-Defined Criteria:
	•	Criteria for selecting a current event (e.g., societal impact, geopolitical significance, cultural resonance).
	•	Criteria for historical events (e.g., relevance, underexplored parallels, diversity of contexts).
	•	Historical Archive Check:
	•	Maintain a log of past pairings to ensure new selections are unique and contribute to the evolving narrative.
	•	Continuity Considerations:
	•	Identify thematic threads or recurring lessons that will connect each edition from one newsletter to the next.
	•	B. Dependencies & Unknowns:
	•	Confirm access to reliable sources for current events and historical archives.
	•	Identify the metrics or qualitative factors (e.g., impact, novelty) that the user wishes to emphasize in the comparison.
	•	Note any unknowns regarding how the current event may evolve over the month.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify the Current Event:
	•	Research:
	•	Scan reputable news outlets, social media, and expert analyses for one major current event with broad impact.
	•	Criteria Filtering:
	•	Evaluate potential events based on relevance, timeliness, and potential for historical comparison.
	•	Output:
	•	A shortlist with a single top candidate selected for the edition.
	•	B. Map the Historical Parallel:
	•	Process:
	1.	Identify historical events that share characteristics or offer instructive contrasts with the current event.
	2.	Assess each candidate for uniqueness, depth, and the potential to enrich the current narrative.
	•	Output:
	•	A selected historical event that most effectively mirrors or contrasts the current event.
	•	C. Flexibility Note:
	•	Unknowns:
	•	The final selections may shift as deeper research is conducted.
	•	The plan includes a mechanism to update the candidate pairing before finalizing the newsletter content.

4. Phase III – In-Depth Comparative Analysis
	•	A. Detailed Investigation of the Pairing:
	•	Sub-Steps for the Current Event:
	1.	Contextual Background:
	•	Outline the causes, impacts, and ongoing developments of the current event.
	2.	Data Collection:
	•	Gather statistics, expert commentary, and real-time updates.
	•	Sub-Steps for the Historical Event:
	1.	Historical Context:
	•	Research the background, causes, and long-term impacts of the historical event.
	2.	Comparative Insights:
	•	Identify key similarities, differences, and lessons that the historical event can illuminate regarding the current event.
	•	B. Integrating the Narrative Across Editions:
	•	Document insights that can serve as recurring themes or “lessons” in subsequent newsletters.
	•	Outline potential narrative connections that link this edition’s pairing to past or future editions (e.g., recurring patterns in leadership responses, economic cycles, social movements).
	•	C. Documentation & Dependency Updates:
	•	Record detailed findings in a living document, noting any areas where further data is required.
	•	Mark any elements that might need updating if new developments occur before publication.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Create a cohesive narrative that explains the significance of both the current and historical events.
	•	Develop visual aids (timelines, comparison charts) to clearly illustrate the parallels and contrasts.
	•	B. Newsletter Structure Alignment:
	•	Main Section:
	•	Event Pairing Analysis: Present the in-depth analysis of the current event and its historical counterpart.
	•	Continuity Section:
	•	Connecting the Dots: Briefly review how this pairing fits into the broader historical narrative established across previous issues.
	•	Optional Supplement:
	•	Lessons Revisited: If applicable, revisit and assess previous pairings in light of new developments.
	•	C. Metrics & Success Criteria:
	•	Define qualitative and quantitative metrics to evaluate the impact and reader engagement (e.g., clarity of insights, reader feedback on relevance, thematic consistency).
	•	Establish benchmarks for how the evolving narrative across editions will be tracked and refined.
	•	D. Plan Dependencies & Flexibility:
	•	Note that final content details will be updated once comprehensive research is complete.
	•	Incorporate user feedback or new data insights to potentially pivot the angle if a more compelling comparison emerges.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Share the preliminary pairing and narrative outline with stakeholders for input.
	•	Schedule review checkpoints:
	•	After candidate identification.
	•	Post in-depth research.
	•	Before final synthesis and newsletter structuring.
	•	B. Flexibility & Future Directions:
	•	Clearly document that the research plan is dynamic and can be adjusted with new insights.
	•	Plan a mechanism to integrate emerging trends or retrospective updates into future editions.
	•	C. Documentation of Gaps:
	•	List any unresolved questions or research gaps, and schedule follow-ups for when additional data becomes available.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Maintain detailed records at every step, ensuring ease of updates and continuity tracking between newsletters.
	•	Scalability & Narrative Continuity:
	•	This modular plan allows each edition to stand alone in its analysis while contributing to an ongoing, connected narrative that evolves from newsletter to newsletter.
	•	Stay open to refining the continuity narrative based on reader feedback and new historical insights.

This execution plan for “Lessons from the Past” ensures that each monthly edition delivers a focused, in-depth comparison of one current event with a historical parallel while building a broader, connected narrative over time. The plan remains flexible, allowing for updates and pivots as new data and insights emerge.
"""

# Creating an instance of NewsletterMetadata for "Historical Echoes: 'Lessons from the Past'"
metadata1 = NewsletterMetadata(
    topic="Historical Echoes: 'Lessons from the Past'",
    title="Historical Echoes",
    target_audience="History enthusiasts, scholars, and the informed public",
    newsletter_goal="Provides historical context for current issues while ensuring thematic continuity over time.",
    desired_tone="Analytical and thought-provoking",
    # Updated content focus to reflect the paired analysis of current and historical events
    content_focus="Each edition examines one significant current event and connects it to one relevant historical event, forming an evolving narrative.",
    # New field: specifying the primary content approach
    content_type="Event Pairing Analysis",
    # New field: specifying the newsletter’s structure
    structure_type="Comparative Analysis",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Concise, analytical, and engaging",
    # New field: recurring themes to maintain narrative continuity
    recurring_themes=["Historical parallels", "Lessons Revisited", "Evolving narratives"],
    generation_frequency=FrequencyEnum.MONTHLY,
    template=None,
    # Updated continuity to incorporate evolving narrative elements
    continuity="Over successive editions, thematic links are maintained by revisiting past comparisons and building on recurring lessons",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="HELP-001",
            publication_date=datetime(2023, 10, 1, 9, 0, 0),
            title="Revisiting the Fall of Empires",
            summary="Explored the decline of ancient empires and drew parallels with modern geopolitical shifts.",
        ),
        PastNewsletter(
            newsletter_id="HELP-002",
            publication_date=datetime(2023, 11, 1, 9, 0, 0),
            title="Echoes of Revolution",
            summary="Compared revolutionary movements of the past with current protests, highlighting recurring patterns.",
        )
    ]
)

topic2 = """
Viral Culture Watch: “Digital Trends Report”

Frequency: Biweekly
Structure: Standard Analysis
Content: Each report examines emerging digital culture trends, such as viral memes, TikTok challenges, or Twitter controversies. It avoids overlap and offers a quarterly retrospective to examine broader social media patterns.
Value: Creates a structured cultural snapshot, avoiding one-off coverage by connecting trends over time.
"""

plan2 = """
Below is a comprehensive, modular research plan for the “Viral Culture Watch: Digital Trends Report.” This plan is designed to provide a clear initial framework while remaining flexible for iterative refinement as new data or insights emerge.

Research Plan: Viral Culture Watch – “Digital Trends Report”

1. Overview & Objectives
	•	Newsletter Topic:
“Digital Trends Report”
	•	Frequency & Structure:
Biweekly, following a Standard Analysis format.
	•	Content Focus:
	•	Examine emerging digital culture trends such as viral memes, TikTok challenges, and Twitter controversies.
	•	Ensure that each edition highlights fresh topics, avoiding overlap with previous reports.
	•	Incorporate a quarterly retrospective to synthesize broader social media patterns over time.
	•	Value Proposition:
Provides readers with a structured cultural snapshot that not only analyzes current digital phenomena but also connects trends over time, offering both immediate insights and long-term contextual understanding.
	•	Key Outcomes:
	•	Identification of one or more emerging digital trends for each biweekly edition.
	•	A clear, engaging analysis that captures the essence and impact of these trends.
	•	A mechanism to link current trends into a broader narrative across quarterly retrospectives.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata
	•	User-Defined Criteria:
	•	Identify key platforms (e.g., TikTok, Twitter, Instagram) where trends are emerging.
	•	Determine metrics for trend selection (e.g., engagement rates, virality, cultural impact).
	•	Specify any additional filters (e.g., regional focus, demographic appeal).
	•	Historical Archive Check:
	•	Maintain an archive of past digital trends covered to avoid redundancy and ensure each report introduces new insights.
	•	Continuity Considerations:
	•	Outline thematic threads that can be tracked over time to feed into the quarterly retrospective, noting recurring cultural patterns.
	•	B. Dependencies & Unknowns:
	•	Secure access to real-time social media analytics and trend aggregation tools.
	•	Identify key data sources (e.g., influencer channels, trend tracking services) and note potential areas where data might be limited or rapidly evolving.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Emerging Trends:
	•	Research Methods:
	•	Scan reputable trend aggregators, social media analytics platforms, and influencer channels for viral content.
	•	Monitor hashtags, engagement metrics, and news feeds related to digital culture.
	•	Criteria Filtering:
	•	Evaluate trends based on engagement, novelty, and potential cultural impact.
	•	Ensure candidates are distinct from topics already covered in previous editions.
	•	Output:
	•	Generate a shortlist of potential trends (e.g., top 3–5 candidates) with the leading candidate earmarked for the upcoming report.
	•	B. Flexibility Note:
	•	The final trend selection is provisional and should be revisited as deeper insights become available.
	•	Document any uncertainties (e.g., rapidly evolving narratives) that may affect final candidate confirmation.

4. Phase III – In-Depth Analysis
	•	A. Detailed Investigation of the Selected Trend:
	•	Contextual Research:
	•	Examine the origins, spread, and current dynamics of the trend.
	•	Identify key influencers, audience reactions, and notable content examples.
	•	Comparative Insights:
	•	Analyze how the trend fits into broader digital culture narratives.
	•	If applicable, compare it with similar past trends to assess its uniqueness and potential longevity.
	•	Data Collection:
	•	Gather quantitative data (e.g., engagement statistics, view counts) and qualitative insights (e.g., expert commentary, audience sentiment).
	•	B. Documenting Findings:
	•	Record all insights in a living document, noting areas that may require updates if the trend evolves before publication.
	•	Highlight any gaps where additional data or expert opinions might be needed.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate the detailed analysis into a cohesive narrative that explains the trend’s cultural significance.
	•	Develop visual aids (charts, infographics, timelines) to enhance reader understanding and engagement.
	•	B. Newsletter Structure Alignment:
	•	Main Analysis Section:
	•	Present the emerging trend, its key characteristics, and its cultural impact.
	•	Continuity & Retrospective Section:
	•	Outline connections to previous trends and indicate how this report contributes to the quarterly retrospective on broader social media patterns.
	•	Optional Additions:
	•	Include short commentary pieces or sidebars that offer additional context or predictions for the trend’s evolution.
	•	C. Metrics & Success Criteria:
	•	Define specific metrics (e.g., reader engagement, social media shares, qualitative feedback) to assess the impact of the report.
	•	Establish benchmarks for the quarterly retrospective to measure how well individual reports contribute to understanding broader trends.
	•	D. Flexibility & Dependencies:
	•	Note that the final content may require adjustments based on emerging data or audience feedback.
	•	Incorporate contingency plans for rapidly changing trends that might necessitate a pivot in focus.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Circulate the preliminary trend analysis and newsletter outline with stakeholders for input.
	•	Set review checkpoints:
	•	After initial trend identification.
	•	Following in-depth analysis.
	•	Prior to final synthesis and structuring.
	•	B. Flexibility & Future Directions:
	•	Document that this research plan is a living document and is open to iterative refinement based on new insights.
	•	Prepare to integrate emerging trends or retrospective insights as part of the evolving narrative across quarterly editions.
	•	C. Documentation of Gaps:
	•	Identify unresolved questions or areas needing further research, and schedule follow-up reviews to address these gaps before publication.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Ensure that every phase of the research process is thoroughly documented, enabling easy updates and transparent handoffs between team members.
	•	Scalability & Narrative Continuity:
	•	This plan allows each biweekly report to function as a standalone analysis while also contributing to a richer, connected narrative over time.
	•	Be prepared to adjust the focus and depth of the analysis based on audience feedback and the rapidly changing nature of digital culture trends.
	•	Next Steps:
	•	Finalize the selection of the emerging trend for the upcoming edition.
	•	Initiate in-depth research and data collection, and schedule the first review session with stakeholders to validate the analysis direction.

This research plan for “Digital Trends Report” establishes a clear, organized approach for capturing emerging digital culture trends while ensuring continuity and depth over time. It balances structured guidance with the flexibility needed to adapt to the fast-evolving nature of digital media.
"""

# Creating an instance of NewsletterMetadata for "Viral Culture Watch: 'Digital Trends Report'"
metadata2 = NewsletterMetadata(
    topic="Viral Culture Watch: 'Digital Trends Report'",
    title="Viral Culture Watch",
    target_audience="Digital culture enthusiasts, social media analysts, and marketing professionals",
    newsletter_goal="Creates a structured cultural snapshot, avoiding one-off coverage by connecting trends over time.",
    desired_tone="Energetic, insightful, and contemporary",
    content_focus="Analysis of emerging digital culture trends such as viral memes, TikTok challenges, and Twitter controversies, with quarterly retrospectives on broader social media patterns.",
    content_type="Standard Analysis",
    structure_type="Standard Analysis",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Concise, modern, and analytical",
    recurring_themes=["Digital culture trends", "Social media patterns", "Viral memes"],
    template=None,
    generation_frequency=FrequencyEnum.BI_WEEKLY,
    continuity="Avoid overlap by connecting current trends with previous analyses and incorporating quarterly retrospectives to examine broader patterns.",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="VCW-001",
            publication_date=datetime(2023, 11, 10, 10, 0, 0),
            title="Meme Mania: The Rise of Viral Trends",
            summary="Analyzed the rapid spread of viral memes and their impact on digital communication.",
        ),
        PastNewsletter(
            newsletter_id="VCW-002",
            publication_date=datetime(2023, 11, 24, 10, 0, 0),
            title="TikTok Takeover: Challenges and Controversies",
            summary="Examined popular TikTok challenges and the controversies they generated.",
        )
    ]
)

topic3 = """
The Next Big Sound: “Emerging Music Trends”

Frequency: Monthly
Structure: Genre-Based Report
Content: Each report highlights 3 new rising artists across different genres, ensuring new selections each time. A “Where Are They Now?” section revisits past predictions, tracking which artists gained mainstream traction.
Value: Establishes an ongoing map of evolving music trends, helping readers discover talent before they blow up.
"""

plan3 = """
Below is a detailed, flexible research plan for the “Emerging Music Trends” newsletter, designed to provide clear guidance at the outset while allowing for iterative refinement as new data or insights emerge.

Research Plan: The Next Big Sound – “Emerging Music Trends”

1. Overview & Objectives
	•	Newsletter Topic:
“Emerging Music Trends”
	•	Frequency & Structure:
Monthly, following a Genre-Based Report format.
	•	Content Focus:
	•	Primary Section: Highlight 3 new rising artists, each representing a different music genre, ensuring a diverse and fresh selection each month.
	•	Supplementary Section: “Where Are They Now?” – Revisits previous predictions to track which artists have broken into mainstream traction, offering a retrospective analysis of past trends.
	•	Value Proposition:
Provides readers with a dynamic map of emerging musical talent, enabling early discovery of promising artists and contextualizing their potential trajectory within evolving music trends.
	•	Key Outcomes:
	•	A curated list of 3 emerging artists, with one from each specified genre.
	•	A structured method for tracking historical predictions and verifying which artists have achieved broader recognition.
	•	A modular framework that can evolve based on reader feedback, genre shifts, or new market trends.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata:
	•	Genre Selection:
	•	Determine key genres to focus on (e.g., pop, hip-hop, indie, electronic, etc.), based on audience interest and current industry dynamics.
	•	Selection Criteria:
	•	Identify metrics for rising talent (e.g., social media buzz, streaming growth, live performance reviews, industry endorsements).
	•	Historical Archive Check:
	•	Compile a list of artists and trends from previous editions to avoid redundancy and to inform the “Where Are They Now?” analysis.
	•	B. Dependencies & Unknowns:
	•	Establish access to industry data sources (e.g., music analytics platforms, streaming reports, social media insights).
	•	Note any gaps in genre representation or emerging subgenres that might need further exploration.
	•	Identify any evolving trends in music discovery that could influence artist selection criteria.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Emerging Artists:
	•	Research Methods:
	•	Monitor music streaming charts, social media platforms, music blogs, and industry newsletters.
	•	Track emerging signals such as rapid audience growth, viral online performances, and buzz on platforms like TikTok or Instagram.
	•	Criteria Filtering:
	•	Evaluate artists based on the defined metrics (e.g., engagement levels, growth in streaming numbers, critical buzz).
	•	Ensure selections are new and distinct from those featured in recent editions.
	•	Output:
	•	A preliminary shortlist of rising artists categorized by genre, with a top 3 selected for the upcoming report.
	•	B. Flexibility Note:
	•	Recognize that final selections may shift as deeper research is conducted.
	•	Document any uncertainties (such as emerging trends in lesser-covered genres) to revisit during later phases.

4. Phase III – In-Depth Analysis
	•	A. Detailed Artist Investigation:
	•	For Each Selected Artist:
	1.	Background Research:
	•	Gather biographical details, current discography, and performance history.
	2.	Market & Cultural Impact:
	•	Analyze social media presence, streaming statistics, and early industry reviews.
	3.	Genre Contextualization:
	•	Place the artist within the current landscape of their genre and identify what makes them stand out.
	•	B. “Where Are They Now?” Section:
	•	Revisit past editions’ selections and track the progress of artists previously identified.
	•	Compare initial predictions with current outcomes, noting key factors that contributed to their success or stagnation.
	•	B. Documentation & Updates:
	•	Record all findings in a living document with clear data points and qualitative insights.
	•	Mark any areas that require updates as trends evolve or additional data becomes available.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate detailed analyses into a cohesive narrative that highlights:
	•	The unique qualities and potential of each emerging artist.
	•	Comparisons across genres to provide readers with a balanced view of the music landscape.
	•	Develop visual aids (e.g., artist timelines, comparative charts) to enhance engagement.
	•	B. Newsletter Structure Alignment:
	•	Main Section:
	•	Present the curated list of 3 emerging artists, with in-depth profiles for each.
	•	Supplementary Section:
	•	“Where Are They Now?” – Offer retrospective insights that connect previous predictions with current industry outcomes.
	•	C. Metrics & Success Criteria:
	•	Define qualitative and quantitative metrics (e.g., reader engagement, social media shares, streaming data) to evaluate the report’s impact.
	•	Establish benchmarks for tracking how well the newsletter helps readers discover rising talent over time.
	•	D. Flexibility & Dependencies:
	•	Note that final content details may need adjustment based on last-minute insights or shifts in music trends.
	•	Plan for periodic updates as new data emerges, ensuring the analysis remains current and relevant.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Circulate the initial research findings and newsletter draft with key stakeholders for feedback.
	•	Schedule review checkpoints:
	•	After initial artist identification.
	•	Post in-depth research.
	•	Prior to final newsletter structuring.
	•	B. Flexibility & Future Directions:
	•	Clearly document that this research plan is a dynamic framework open to iterative refinement.
	•	Incorporate reader feedback and industry developments to potentially adjust genre focus or selection criteria in future editions.
	•	C. Documentation of Gaps:
	•	List any unresolved questions or data gaps and schedule follow-up research sessions to address these before publication.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Maintain detailed records of research processes, selection criteria, and analytical findings for transparency and future reference.
	•	Scalability & Narrative Continuity:
	•	Ensure that each monthly edition stands alone as a robust analysis while contributing to an ongoing, connected narrative of emerging music trends.
	•	Use the “Where Are They Now?” section to bridge past and present, deepening the reader’s engagement with the evolving music landscape.
	•	Next Steps:
	•	Finalize the shortlist of emerging artists for the upcoming edition.
	•	Initiate in-depth research on each artist and begin drafting the main and supplementary sections.
	•	Set up a review meeting with stakeholders to confirm the direction and ensure all data gaps are addressed.

This research plan for “Emerging Music Trends” provides a structured yet adaptable framework to uncover and analyze rising musical talent while tracking historical predictions. It is designed to help readers discover new artists before they achieve mainstream success, and to refine the analysis iteratively as the music landscape evolves.
"""

metadata3 = NewsletterMetadata(
    topic="The Next Big Sound: 'Emerging Music Trends'",
    title="The Next Big Sound",
    target_audience="Music aficionados, industry insiders, and aspiring artists",
    newsletter_goal="Establishes an ongoing map of evolving music trends, helping readers discover talent before they blow up.",
    desired_tone="Vibrant, inspiring, and forward-thinking",
    content_focus="Genre-based report spotlighting 3 new rising artists with a 'Where Are They Now?' follow-up on past predictions.",
    content_type="Genre-Based Report",
    structure_type="Genre-Based Report",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Dynamic and narrative, blending vivid storytelling with analytical insights",
    recurring_themes=["Emerging music trends", "Historical predictions", "Music industry insights"],
    template="""
    <template>
        <title>
            {{title}}
        </title>
        <content>
            {{info on rising artist 1}}
            {{info on rising artist 2}}
            {{info on rising artist 3}}
        </content>
        <where_are_they_now>
            {{info on where they are now}}
        </where_are_they_now>
    """,
    generation_frequency=FrequencyEnum.MONTHLY,
    continuity="Builds on past predictions by revisiting previous artist spotlights in the 'Where Are They Now?' section to track progress over time.",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="NBS-001",
            publication_date=datetime(2023, 12, 1, 10, 0, 0),
            title="Sound Beginnings: Rising Stars to Watch",
            summary="Featured three emerging artists (named Bruno Mars, Lana Del Rey, and Kendrick Lamar) from pop, indie, and electronic genres, forecasting their potential breakthrough.",
        )
    ]
)

topic4 = """
Founder Spotlight: “The Startup Diaries”

Frequency: Monthly
Structure: Ongoing Founder Stories (Diary Format)
Content: Each edition tracks 3-5 startup founders, providing diary-style updates on their progress. Instead of standalone interviews, this format follows their journey over time, making it feel like a real-time docuseries on entrepreneurship.
Value: Gives readers an evolving narrative on startup challenges and victories, rather than just isolated insights.
"""

plan4 = """
Below is a detailed, flexible research plan for “The Startup Diaries,” designed to capture the ongoing journeys of startup founders through a diary-style format while allowing room for iterative refinement as new insights and data emerge.

Research Plan: Founder Spotlight – “The Startup Diaries”

1. Overview & Objectives
	•	Newsletter Topic:
“The Startup Diaries”
	•	Frequency & Structure:
Monthly, following an ongoing Founder Stories (Diary Format) approach.
	•	Content Focus:
	•	Primary Section: Track 3-5 startup founders, offering diary-style updates on their progress, challenges, and victories.
	•	Narrative Approach: Rather than standalone interviews, the content is presented as a continuous, evolving narrative that follows each founder’s journey over time.
	•	Value Proposition: Provides readers with an immersive, real-time docuseries feel, delivering deeper insights into the entrepreneurial process and ongoing startup dynamics.
	•	Key Outcomes:
	•	A curated list of 3-5 startup founders to follow each month.
	•	Regular, updated profiles that capture the progress and evolving narratives of these founders.
	•	A dynamic archive that builds a rich, longitudinal story of startup challenges, pivots, and successes.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata:
	•	Founder Selection Criteria:
	•	Identify promising startups based on early traction, innovative business models, or recent funding milestones.
	•	Consider diversity in industry, stage, and geographic representation to offer a varied narrative.
	•	Data Sources & Tools:
	•	Utilize startup databases, accelerator program updates, industry newsletters, and social media channels for founder insights.
	•	Historical Archive Check:
	•	Maintain records of past founder profiles to avoid redundancy and to provide context for “diary” updates.
	•	B. Dependencies & Unknowns:
	•	Establish reliable channels to receive regular updates from selected founders (e.g., direct outreach, social media, or public announcements).
	•	Identify potential gaps in available data or changes in founder availability that might require alternative approaches.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Startup Founders:
	•	Research Methods:
	•	Monitor startup news, funding announcements, and entrepreneurial events to spot rising founders.
	•	Engage with startup incubators, accelerators, and venture capital updates for recommendations.
	•	Criteria Filtering:
	•	Evaluate founders based on growth potential, recent milestones, and willingness to share ongoing insights.
	•	Ensure that the selected founders offer fresh, diverse perspectives not recently covered in previous editions.
	•	Output:
	•	Create a shortlist of 3-5 founders to be featured in the upcoming edition, with initial profiles outlining their startup’s vision, current status, and recent developments.
	•	B. Flexibility Note:
	•	Recognize that the final list may evolve as deeper research uncovers additional context or as startups experience rapid changes.
	•	Document any uncertainties (such as pending funding rounds or unconfirmed updates) to revisit in subsequent editions.

4. Phase III – In-Depth Analysis & Diary Updates
	•	A. Detailed Founder Profiling:
	•	For Each Selected Founder:
	1.	Background & Context:
	•	Gather comprehensive background information including the startup’s origin story, mission, and early challenges.
	2.	Current Developments:
	•	Track key metrics such as funding updates, product launches, user growth, and pivots.
	3.	Narrative Elements:
	•	Document personal insights, direct quotes, and diary-style entries that reflect their day-to-day experiences.
	•	B. Ongoing Diary Update Process:
	•	Develop a system for regular check-ins (e.g., weekly or biweekly updates) that feed into the monthly newsletter.
	•	Note recurring themes or turning points in each founder’s journey that add depth to the evolving narrative.
	•	C. Documentation & Dependency Updates:
	•	Record all insights and updates in a centralized document to create a living archive.
	•	Identify any areas that require additional follow-up or where further data (e.g., direct interviews) might enhance the narrative.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate the detailed updates into a cohesive monthly narrative that reflects each founder’s journey.
	•	Develop visual aids (timelines, progress charts) to illustrate key milestones and narrative arcs.
	•	B. Newsletter Structure Alignment:
	•	Main Section:
	•	Present diary-style updates for each founder, including insights into recent challenges, successes, and personal reflections.
	•	Continuity Section:
	•	Highlight how current updates connect with past editions, reinforcing the ongoing narrative of each founder’s journey.
	•	C. Metrics & Success Criteria:
	•	Define key performance indicators such as reader engagement, follow-through on founder stories, and feedback on the narrative quality.
	•	Set benchmarks to evaluate the evolution of each founder’s story and the overall impact of the newsletter on reader insights into entrepreneurship.
	•	D. Flexibility & Dependencies:
	•	Note that final content details may shift based on emerging developments or new founder insights.
	•	Allow for iterative updates in the “diary” sections as new data becomes available, ensuring the narrative remains current and engaging.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Circulate the initial founder profiles and diary update outlines with key stakeholders for input.
	•	Schedule review checkpoints:
	•	After initial founder identification.
	•	Post in-depth research and diary updates.
	•	Prior to final newsletter structuring.
	•	B. Flexibility & Future Directions:
	•	Clearly document that this research plan is a living document, adaptable based on new insights or reader feedback.
	•	Be prepared to adjust founder selections or narrative angles as the startup landscape evolves.
	•	C. Documentation of Gaps:
	•	Identify any unresolved questions or data gaps (e.g., missing founder insights, pending updates) and plan follow-up research sessions to address these before publication.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Ensure that every step—from founder selection to diary updates—is meticulously recorded to facilitate smooth updates and narrative continuity.
	•	Scalability & Narrative Continuity:
	•	This modular plan is designed so that each monthly edition serves as a standalone update while contributing to an ongoing, interconnected narrative on startup journeys.
	•	Use the evolving diary format to deepen reader engagement and provide a real-time view of entrepreneurial challenges and triumphs.
	•	Next Steps:
	•	Finalize the shortlist of startup founders for the upcoming edition.
	•	Initiate in-depth research and establish a schedule for regular diary updates.
	•	Organize a review session with stakeholders to validate the initial narratives and confirm data sources.

This research plan for “The Startup Diaries” strikes the balance between providing a clear, structured roadmap for tracking startup founder journeys and remaining flexible to accommodate the evolving nature of entrepreneurship. It is designed to deliver engaging, diary-style narratives that keep readers connected to the dynamic world of startups over time.
"""
metadata4 = NewsletterMetadata(
    topic="Founder Spotlight: 'The Startup Diaries'",
    title="The Startup Diaries",
    target_audience="Aspiring entrepreneurs, startup enthusiasts, and venture capitalists",
    newsletter_goal="Provides an evolving narrative on startup challenges and victories by tracking founders' journeys in a diary-style, real-time docuseries format.",
    desired_tone="Intimate, candid, and inspirational",
    content_focus="Diary-style updates following 3-5 startup founders over multiple editions, capturing their evolving challenges and successes.",
    content_type="Founder Stories (Diary Format)",
    structure_type="Founder Stories (Diary Format)",
    desired_length=LengthEnum.LONG,
    preferred_writing_style="Conversational and narrative, emphasizing real-time updates and personal insights",
    recurring_themes=["Startup challenges", "Entrepreneurial victories", "Real-time updates"],
    template=None,
    generation_frequency=FrequencyEnum.MONTHLY,
    continuity="Maintains an ongoing narrative by tracking founders' progress across editions",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="FS-001",
            publication_date=datetime(2023, 12, 15, 10, 0, 0),
            title="Diaries Begin: The Journey of a First-Time Founder",
            summary="Introduced the inaugural profile of a tech startup founder, documenting early challenges and aspirations in a diary-style narrative.",
        )
    ]
)

topic5 = """
The Social Media Playbook: “Strategic Case Studies”

Frequency: Weekly
Structure: Playbook & Case Study Format
Content: Each report dissects a successful marketing campaign, influencer strategy, or viral growth tactic, turning it into a step-by-step strategy guide. The system ensures no repeated examples while tracking larger digital behavior shifts over time.
Value: Makes social media insights actionable, turning reports into a practical toolkit rather than just analysis.
"""

plan5 = """
Below is a detailed and adaptable research plan for “The Social Media Playbook: Strategic Case Studies.” This plan offers a clear framework from the outset while remaining flexible for further refinement, updates, or even pivoting based on emerging insights and data.

Research Plan: The Social Media Playbook – “Strategic Case Studies”

1. Overview & Objectives
	•	Newsletter Topic:
“Strategic Case Studies” – dissecting successful marketing campaigns, influencer strategies, or viral growth tactics.
	•	Frequency & Structure:
Weekly, utilizing a Playbook & Case Study Format.
	•	Content Focus:
	•	Primary Analysis: Each edition will break down one successful strategy into a step-by-step guide, detailing key tactics, execution methods, and outcomes.
	•	Actionability: The goal is to translate the case study into a practical toolkit that readers can apply to their own social media and marketing efforts.
	•	Trend Tracking: Over time, the plan will ensure that examples do not repeat and will map larger shifts in digital behavior.
	•	Value Proposition:
Transforms social media insights into actionable strategies, giving readers a practical playbook that evolves with broader digital trends.
	•	Key Outcomes:
	•	A curated, non-redundant list of case studies drawn from successful campaigns or strategies.
	•	Detailed step-by-step breakdowns that provide readers with a clear guide on how to replicate or adapt these strategies.
	•	An ongoing narrative that links individual case studies to emerging digital trends.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata:
	•	Selection Criteria:
	•	Identify campaigns, influencer strategies, or viral tactics that have demonstrable success metrics (e.g., engagement rates, conversion rates, audience growth).
	•	Determine qualitative criteria (e.g., creativity, relevance, and replicability).
	•	Historical Archive Check:
	•	Maintain an up-to-date archive of previously analyzed case studies to prevent repetition and provide historical context.
	•	User-Defined Filters:
	•	Specify any additional filters such as industry, geographic focus, or target demographic, as required by the audience.
	•	B. Dependencies & Unknowns:
	•	Identify reliable data sources and platforms (social media analytics, campaign reports, influencer case studies, etc.).
	•	Note potential gaps in data, especially for rapidly evolving digital strategies or less-documented campaigns.
	•	Ensure access to expert commentary or interviews if deeper insights are needed.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Candidate Strategies:
	•	Research Methods:
	•	Monitor industry news, social media trend reports, and digital marketing award winners.
	•	Leverage social listening tools and analytics platforms to spot campaigns or strategies showing notable results.
	•	Criteria Filtering:
	•	Evaluate candidates based on impact metrics (e.g., viral spread, ROI, conversion figures) and narrative potential.
	•	Ensure that the selected candidate is distinct from previous editions to maintain freshness.
	•	Output:
	•	Develop a shortlist of potential case studies, then finalize one candidate per weekly edition as the focus.
	•	B. Flexibility Note:
	•	Acknowledge that candidate selection may evolve with new data or emerging trends.
	•	Document any uncertainties (such as rapidly changing campaign outcomes) that might necessitate a pivot before finalizing the case study.

4. Phase III – In-Depth Analysis
	•	A. Detailed Case Study Research:
	•	Campaign Overview:
	•	Gather comprehensive data on the selected strategy including objectives, target audience, execution methods, and key performance metrics.
	•	Step-by-Step Breakdown:
	•	Decompose the strategy into actionable steps: planning, execution, monitoring, and optimization phases.
	•	Expert Insights:
	•	Supplement with interviews or commentary from industry experts, campaign managers, or influencers involved.
	•	Comparative Context:
	•	Contrast with similar campaigns if relevant, noting unique elements and best practices.
	•	B. Documentation & Data Verification:
	•	Record findings in a detailed, centralized document to ensure all insights are captured.
	•	Validate data points with multiple sources to ensure reliability, especially if drawing on fast-changing digital metrics.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate the step-by-step breakdown into a cohesive narrative that highlights the key takeaways and actionable strategies.
	•	Develop visual aids (e.g., flowcharts, checklists, or infographics) that illustrate the process and key metrics.
	•	B. Newsletter Structure Alignment:
	•	Main Section:
	•	Present the case study in a clear, structured format that guides readers through the campaign strategy and its execution.
	•	Actionable Playbook:
	•	Include a “How to Apply” segment that translates the case study into a practical toolkit for readers.
	•	Trend Context:
	•	Briefly connect the case study to broader digital behavior shifts, setting the stage for ongoing narrative continuity.
	•	C. Metrics & Success Criteria:
	•	Define key performance indicators such as reader engagement, actionable feedback, and practical implementation success.
	•	Establish benchmarks to track the evolution of digital strategy trends over time as more case studies are published.
	•	D. Flexibility & Dependencies:
	•	Note that final content may require adjustments based on late-breaking insights or additional data.
	•	Allow room for iterative updates, especially if subsequent reviews reveal new angles or opportunities for deeper analysis.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Circulate the draft case study and playbook outline with stakeholders or industry experts for input.
	•	Schedule review checkpoints:
	•	After initial candidate identification.
	•	Post in-depth analysis and data synthesis.
	•	Prior to final newsletter structuring.
	•	B. Flexibility & Future Directions:
	•	Clearly document that this plan is a living document, with adjustments welcomed based on reader feedback and evolving digital trends.
	•	Prepare to integrate new case studies or pivot the approach if more impactful strategies emerge.
	•	C. Documentation of Gaps:
	•	Identify any unresolved questions or data gaps and schedule follow-up research sessions to address these before final publication.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Maintain detailed records of research processes, source data, and analytical insights to ensure transparency and facilitate future updates.
	•	Scalability & Narrative Continuity:
	•	Ensure that each weekly edition stands alone as a comprehensive case study while contributing to a broader understanding of shifting digital behaviors over time.
	•	Next Steps:
	•	Finalize the candidate for the upcoming edition.
	•	Begin in-depth analysis and data collection for the selected case study.
	•	Organize a review session with stakeholders to confirm the final direction and address any outstanding research gaps.

This research plan for “The Social Media Playbook: Strategic Case Studies” balances a clear, structured approach with the flexibility necessary to adapt to rapidly changing digital trends and emerging insights. It is designed to transform successful marketing tactics into actionable guides, ensuring each weekly edition provides practical value and contributes to a growing strategic toolkit for readers.

"""

metadata5 = NewsletterMetadata(
    topic="The Social Media Playbook: 'Strategic Case Studies'",
    title="The Social Media Playbook",
    target_audience="Marketing professionals, social media strategists, and brand managers",
    newsletter_goal="Makes social media insights actionable by turning case studies into a practical step-by-step strategy guide.",
    desired_tone="Practical, insightful, and energetic",
    content_focus="Detailed dissection of successful marketing campaigns, influencer strategies, or viral growth tactics with step-by-step breakdowns.",
    content_type="Strategic Case Studies",
    structure_type="Strategic Case Studies",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Clear and instructive, combining analysis with actionable advice",
    recurring_themes=["Successful marketing campaigns", "Influencer strategies", "Viral growth tactics"],
    template="""
    <template>
        <title>
            {{title}}
        </title>
        <case_study>
            {{details on the successful campaign or strategy}}
        </case_study>
        <strategy_steps>
            {{step-by-step breakdown of the approach}}
        </strategy_steps>
        <key_insights>
            {{actionable insights for replication}}
        </key_insights>
    </template>
    """,
    generation_frequency=FrequencyEnum.WEEKLY,
    continuity="Ensures no repeated examples and tracks evolving digital behavior shifts over time",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="SM-001",
            publication_date=datetime(2023, 12, 20, 9, 30, 0),
            title="Unlocking Viral Success: The Case of the Unexpected Campaign",
            summary="Dissected a breakthrough campaign that leveraged unconventional strategies to achieve viral growth.",
        )
    ]
)

topic6 = """
The Global Climate Report: “An Investigative Series”

Frequency: Quarterly
Structure: Long-Form Investigative Journalism
Content: Instead of a data dump, this report takes a deep-dive storytelling approach, blending firsthand reports, expert interviews, and real-world case studies. Each edition connects to prior investigations, forming an evolving climate research archive.
Value: Turns climate reporting into a compelling, human-centered narrative, engaging readers beyond just statistics.
"""

plan6 = """
Below is a comprehensive, adaptable research plan for “The Global Climate Report: An Investigative Series.” This plan provides a clear framework to begin your in-depth climate investigation while leaving ample room for iterative updates, refinements, and new directions as emerging data and insights dictate.

Research Plan: The Global Climate Report – “An Investigative Series”

1. Overview & Objectives
	•	Newsletter Topic:
“The Global Climate Report”
	•	Frequency & Structure:
Quarterly, following a Long-Form Investigative Journalism format.
	•	Content Focus:
	•	Deep-Dive Storytelling: Each edition features an immersive narrative that blends firsthand reporting, expert interviews, and real-world case studies.
	•	Archival Connectivity: Connects current investigations to prior reports, building a continuous, evolving climate research archive.
	•	Human-Centered Approach: Focus on engaging readers through compelling storytelling beyond raw data.
	•	Value Proposition:
Transforms climate reporting into a captivating, human-centered narrative that offers both rigorous investigation and emotional resonance, engaging readers with insights that go far beyond statistics.
	•	Key Outcomes:
	•	Identification of a primary climate issue or event for the edition.
	•	Comprehensive, multifaceted investigation combining personal stories, expert perspectives, and field data.
	•	An evolving archive that links current findings to past investigations, creating a long-term narrative on global climate issues.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata:
	•	Topic Scope:
	•	Define the central climate issue, region, or phenomenon to investigate (e.g., extreme weather events, policy impacts, community resilience).
	•	Establish thematic boundaries (e.g., scientific, socio-political, economic) based on audience interest.
	•	User-Defined Criteria:
	•	Include criteria for selecting case studies, interviews, and firsthand reports (e.g., relevance, impact, novelty).
	•	Historical Archive Check:
	•	Review previous climate investigations to maintain narrative continuity and avoid redundancy.
	•	Data Source Identification:
	•	List primary sources (e.g., climate research institutes, government reports, local news, firsthand accounts).
	•	B. Dependencies & Unknowns:
	•	Confirm access to expert contacts, field reporters, and reliable data sets.
	•	Identify potential gaps in available data or areas requiring further investigation (e.g., regions with limited reporting).
	•	Note that evolving climate events may influence the final scope of the investigation.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Key Climate Issues/Events:
	•	Broad Research:
	•	Monitor global climate news, scientific publications, and policy updates to spot emerging issues.
	•	Candidate Selection:
	•	Develop a shortlist of high-impact events or topics based on relevance, urgency, and narrative potential.
	•	Evaluate candidates using qualitative and quantitative metrics (e.g., severity, public impact, scientific consensus).
	•	B. Flexibility Note:
	•	Recognize that the final topic selection may shift as further data is gathered.
	•	Document uncertainties (e.g., rapidly evolving events, incomplete data) for follow-up investigation.

4. Phase III – In-Depth Investigation & Analysis
	•	A. Detailed Field Investigation:
	•	Firsthand Reporting:
	•	Organize field visits or virtual interviews to collect on-the-ground accounts and personal stories.
	•	Expert Interviews:
	•	Schedule interviews with climate scientists, policy experts, and affected community leaders to provide authoritative insights.
	•	Case Study Analysis:
	•	Collect real-world examples and historical case studies that mirror or contrast the current climate issue.
	•	Data Verification:
	•	Cross-check facts, statistics, and expert opinions with multiple reliable sources.
	•	B. Documentation & Continuous Updates:
	•	Record all findings in a living document to facilitate updates as the investigation evolves.
	•	Note any emerging trends or new insights that may adjust the narrative direction before final synthesis.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate firsthand reports, expert insights, and case studies into a cohesive, compelling narrative.
	•	Develop visual aids (e.g., maps, timelines, infographics) to complement the storytelling and clarify complex data.
	•	B. Newsletter Structure Alignment:
	•	Main Investigative Feature:
	•	Present the core investigative narrative, detailing the selected climate issue with a human-centered approach.
	•	Connecting Past & Present:
	•	Include a segment that ties the current report to previous investigations, reinforcing an evolving climate research archive.
	•	Storytelling Enhancements:
	•	Use narrative techniques such as character-driven storytelling, descriptive language, and contextual background to engage readers.
	•	C. Metrics & Success Criteria:
	•	Define engagement metrics (e.g., reader feedback, social media shares, and follow-up discussions).
	•	Establish benchmarks for narrative impact and the effectiveness of integrating expert and firsthand perspectives.
	•	D. Flexibility & Dependencies:
	•	Allow for iterative revisions based on late-breaking developments or newly available data.
	•	Prepare contingency strategies for pivoting the narrative if new angles or significant updates emerge during the investigation.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Share preliminary findings and the draft narrative with key stakeholders and subject-matter experts.
	•	Schedule review checkpoints:
	•	After initial data collection and candidate selection.
	•	Post in-depth investigation and before final synthesis.
	•	Prior to final layout and publication.
	•	B. Flexibility & Future Directions:
	•	Clearly document that this investigative plan is dynamic, with built-in opportunities for refinement.
	•	Be prepared to integrate emerging data or pivot the investigation’s focus as the climate situation evolves.
	•	C. Documentation of Gaps:
	•	List unresolved questions or research gaps and schedule follow-up sessions to address these before publication.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Maintain detailed records of all investigative steps, source data, and interview transcripts to ensure transparency and ease future reference.
	•	Scalability & Narrative Continuity:
	•	Design the report to serve as both a standalone deep-dive and part of an ongoing, interconnected climate narrative.
	•	Use the evolving archive of investigations to build a long-term resource that enhances reader understanding over multiple editions.
	•	Next Steps:
	•	Finalize the selection of the primary climate issue for the upcoming edition.
	•	Initiate field reporting, schedule expert interviews, and begin collecting related case studies.
	•	Organize an initial review session with stakeholders to validate the investigation’s scope and adjust for any emerging insights.

This research plan for “The Global Climate Report: An Investigative Series” provides a robust, clear roadmap for producing a long-form, human-centered climate investigation. It balances structured planning with the flexibility needed to refine the narrative as new insights emerge, ensuring that each quarterly edition contributes meaningfully to a growing, interconnected archive of climate research.
"""

metadata6 = NewsletterMetadata(
    topic="The Global Climate Report: 'An Investigative Series'",
    title="The Global Climate Report",
    target_audience="Environmental advocates, climate researchers, policy makers, and informed citizens",
    newsletter_goal=(
        "Turns climate reporting into a compelling, human-centered narrative by blending "
        "in-depth storytelling, expert interviews, and real-world case studies into a continuous investigative archive."
    ),
    desired_tone="Serious, in-depth, and empathetic",
    content_focus=(
        "Long-form investigative journalism that combines firsthand reports, expert insights, "
        "and case studies to create an evolving climate research narrative."
    ),
    content_type="Investigative Series",
    structure_type="Investigative Series",
    desired_length=LengthEnum.LONG,
    preferred_writing_style="Narrative-driven, detailed, and immersive",
    recurring_themes=["Climate change", "Environmental issues", "Climate science"],
    template=None,
    generation_frequency=FrequencyEnum.QUARTERLY,
    continuity="Connects current investigations with previous reports to form a continuous climate research archive",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="GCR-001",
            publication_date=datetime(2023, 3, 15, 12, 0, 0),
            title="Unraveling the Arctic Meltdown",
            summary=(
                "An in-depth exploration of the rapid changes in the Arctic, featuring interviews with climatologists "
                "and indigenous perspectives."
            ),
        ),
        PastNewsletter(
            newsletter_id="GCR-002",
            publication_date=datetime(2023, 6, 15, 12, 0, 0),
            title="Deforestation Diaries: The Amazon at Risk",
            summary=(
                "Investigative report on the accelerating deforestation in the Amazon and its global implications, "
                "supported by satellite imagery and local accounts."
            ),
        ),
        PastNewsletter(
            newsletter_id="GCR-003",
            publication_date=datetime(2023, 9, 15, 12, 0, 0),
            title="Rising Tide: Coastal Erosion and Climate Refugees",
            summary=(
                "Documented the effects of rising sea levels on coastal communities and the emerging crisis of "
                "climate-induced displacement."
            ),
        )
    ]
)

topic7 = """
The Evolution of Strategy: “Coach’s Notebook”

Frequency: Weekly
Structure: First-Person Tactical Breakdown
Content: Instead of an external analysis, each edition is framed as a fictionalized “coaching journal”—an insider-style breakdown of sports tactics, strategy shifts, and real-time decision-making. If requested, a “Season Tracker” could show how teams evolve over time.
Value: Makes sports analysis immersive, letting readers experience strategy as if they were in the game.
"""

plan7 = """
Below is a comprehensive, adaptable research plan for “Coach’s Notebook – The Evolution of Strategy.” This plan provides a clear framework to kick off your weekly, first-person tactical breakdown while leaving room to adjust, refine, or pivot as needed based on emerging data, game developments, or reader feedback.

Research Plan: The Evolution of Strategy – “Coach’s Notebook”

1. Overview & Objectives
	•	Newsletter Topic:
“Coach’s Notebook” – a first-person, fictionalized coaching journal offering insider-style tactical breakdowns, strategy shifts, and real-time decision-making in sports.
	•	Frequency & Structure:
Weekly editions presented in a diary-style format. Optionally, include a “Season Tracker” section to monitor how teams evolve over time.
	•	Content Focus:
	•	Primary Narrative: Each issue is framed as an insider’s account from the “coach’s” perspective, detailing tactical decisions, strategy evolutions, and in-game adjustments.
	•	Optional Supplement: The “Season Tracker” offers longitudinal insights, connecting the dots between weekly analyses and showing overall team progress or strategic shifts.
	•	Value Proposition:
Provides an immersive, game-like experience, enabling readers to feel as though they’re part of the strategic planning process—delivering actionable sports insights and an engaging narrative that goes beyond conventional analysis.
	•	Key Outcomes:
	•	A recurring set of tactical breakdowns that detail specific game scenarios and strategic decisions.
	•	A clear, engaging narrative voice that evolves over time.
	•	A dynamic archive that tracks broader season trends and team evolution.

2. Phase I – Context & Metadata Setup
	•	A. Define Parameters & Metadata:
	•	Target Sports & Leagues:
	•	Identify the sports or leagues to focus on (e.g., football, basketball, soccer), based on audience interests and available data.
	•	Narrative Tone:
	•	Establish the first-person, fictionalized coaching persona, including key stylistic elements (e.g., authoritative yet relatable, strategic insight with a personal touch).
	•	Historical Data & Archives:
	•	Create an archive of previous tactical breakdowns and season summaries to ensure continuity and avoid repetition.
	•	B. Dependencies & Unknowns:
	•	Secure access to game footage, play-by-play data, and expert tactical analyses.
	•	Identify primary sources for real-time sports data (e.g., live stats, analyst reports).
	•	Note any uncertainties (e.g., sudden game developments, injuries, or unexpected strategy shifts) that may influence narrative adjustments.

3. Phase II – Initial Research & Candidate Identification
	•	A. Identify Key Game Events & Tactical Scenarios:
	•	Research Methods:
	•	Monitor upcoming games, notable matchups, and key tactical battles that promise rich strategic narratives.
	•	Use sports analytics platforms, expert commentary, and live game tracking to select candidates.
	•	Criteria Filtering:
	•	Evaluate games based on their tactical complexity, potential for strategic insight, and overall excitement.
	•	Ensure each edition spotlights a distinct scenario to maintain variety across issues.
	•	Output:
	•	Generate a shortlist of game events or tactical moments to serve as the focal point for each weekly edition.
	•	B. Flexibility Note:
	•	Remain open to last-minute changes based on unexpected game developments.
	•	Document any uncertainties or evolving situations that may require updates to the chosen narrative before publication.

4. Phase III – In-Depth Tactical Analysis & Diary Updates
	•	A. Detailed Investigation & Breakdown:
	•	Tactical Analysis:
	•	Deep-dive into the selected game or event, dissecting key decisions, formations, and in-game adjustments.
	•	Gather qualitative data from post-game analyses, expert interviews, and statistical reports.
	•	First-Person Narrative Construction:
	•	Craft a diary-style account from the “coach’s” perspective, incorporating both factual breakdowns and personal insights.
	•	Emphasize decision-making rationale, challenges faced, and lessons learned in a way that feels authentic and immersive.
	•	B. Season Tracker Integration (Optional):
	•	If requested, compile ongoing updates that reflect broader team evolution and strategy trends over the course of the season.
	•	Establish benchmarks (e.g., key performance indicators, pivotal games) that inform the “Season Tracker” narrative.
	•	C. Documentation & Data Verification:
	•	Maintain a central document logging all key tactical insights, game data, and narrative notes.
	•	Validate the analysis through cross-referencing multiple sources to ensure accuracy and depth.

5. Phase IV – Synthesis & Newsletter Structuring
	•	A. Data Synthesis:
	•	Integrate the tactical breakdown and narrative insights into a coherent, engaging story.
	•	Develop supporting visuals such as play diagrams, timelines, and annotated game clips to enhance the analysis.
	•	B. Newsletter Structure Alignment:
	•	Main Section:
	•	Present the “Coach’s Notebook” narrative, offering a step-by-step breakdown of the tactical decision-making process.
	•	Optional Section:
	•	“Season Tracker” – Provide updates on overall team strategy and evolution, linking the current edition with previous insights.
	•	C. Metrics & Success Criteria:
	•	Define key performance indicators such as reader engagement, actionable feedback, and narrative clarity.
	•	Set benchmarks to assess the evolving narrative and its impact on reader understanding of sports strategy.
	•	D. Flexibility & Dependencies:
	•	Note that final narrative details may need adjustments based on late-breaking insights or reader feedback.
	•	Build in mechanisms for iterative revisions to ensure the story remains current and compelling.

6. Phase V – Iteration & Finalization
	•	A. Review & Feedback Loop:
	•	Share draft editions with stakeholders, sports analysts, or target readers for constructive feedback.
	•	Schedule review checkpoints:
	•	After candidate selection.
	•	Post in-depth analysis and narrative drafting.
	•	Prior to final layout and publication.
	•	B. Flexibility & Future Directions:
	•	Clearly document that the research plan is a living document, ready to be refined based on new sports developments or shifts in reader interests.
	•	Prepare contingency strategies for unexpected game events that could alter the planned narrative.
	•	C. Documentation of Gaps:
	•	Identify any unresolved questions (e.g., additional tactical data needed, alternate perspectives) and schedule follow-up research sessions to address these before finalization.

7. Final Notes & Next Steps
	•	Comprehensive Documentation:
	•	Keep detailed records of all research, narrative drafts, and tactical analyses to ensure transparency and ease of future updates.
	•	Scalability & Narrative Continuity:
	•	Ensure that each weekly edition functions as a standalone tactical breakdown while contributing to a broader, evolving narrative on sports strategy.
	•	Use the “Season Tracker” to create continuity, linking past analyses with current game insights.
	•	Next Steps:
	•	Finalize the selection of the upcoming game/event to focus on.
	•	Initiate in-depth tactical analysis and draft the corresponding diary narrative.
	•	Organize a review session with stakeholders to validate the narrative direction and address any outstanding research gaps.

This research plan for “Coach’s Notebook – The Evolution of Strategy” provides a clear, structured approach to producing immersive, first-person sports analysis. It balances detailed tactical breakdowns with the flexibility needed to adjust to real-time game developments and evolving reader interests, ensuring each weekly edition delivers actionable insights and a dynamic narrative experience.
"""
# Creating an instance of NewsletterMetadata for "The Evolution of Strategy: 'Coach’s Notebook'"
metadata7 = NewsletterMetadata(
    topic="The Evolution of Strategy: 'Coach’s Notebook'",
    title="The Evolution of Strategy",
    target_audience="Sports enthusiasts, coaches, players, and tactical analysts",
    newsletter_goal="Provides an immersive, insider view of sports strategy through a first-person coaching journal narrative, letting readers experience game-day decision-making as if they were on the field.",
    desired_tone="Intimate, tactical, and engaging",
    content_focus="A first-person tactical breakdown and real-time analysis of sports strategies, with a focus on in-game decisions and evolving team dynamics.",
    content_type="First-Person Tactical Breakdown",
    structure_type="First-Person Tactical Breakdown",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Conversational and detailed, blending personal insights with technical analysis",
    recurring_themes=["Sports strategy", "Game-day decisions", "Team dynamics"],
    template="""
    <template>
        <header>
            <title>{{title}}</title>
            <game_date>{{game_date}}</game_date>
            <opponent>{{opponent}}</opponent>
        </header>
        <strategy_journal>
            <tactical_analysis>{{tactical_analysis}}</tactical_analysis>
            <real_time_decision>{{real_time_decision}}</real_time_decision>
        </strategy_journal>
        <season_tracker>
            <update>{{season_update}}</update>
        </season_tracker>
    </template>
    """,
    generation_frequency=FrequencyEnum.WEEKLY,
    continuity="Maintains an evolving narrative of team strategy and tactical adjustments throughout the season",
    past_newsletters=[]
)