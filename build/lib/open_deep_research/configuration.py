import os
from enum import Enum
from dataclasses import dataclass, field, fields
from typing import Any, Optional, List

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from dataclasses import dataclass
from datetime import datetime
from src.open_deep_research.newsletter_state import NewsletterMetadata, LengthEnum, FrequencyEnum, PastNewsletter

DEFAULT_REPORT_STRUCTURE = """
No default report structure. Come up with a structure that makes sense for the user's topic.
"""

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"

class PlannerProvider(Enum):
    OPENAI = "openai"
    GROQ = "groq"

def create_default_newsletter_metadata() -> NewsletterMetadata:
    """Create a default NewsletterMetadata instance."""
    # return NewsletterMetadata(
    #     topic="Historical Echoes: 'Lessons from the Past'",
    #     title="Historical Echoes",
    #     target_audience="History enthusiasts, scholars, and the informed public",
    #     newsletter_goal="Provides historical context for current issues while ensuring thematic continuity over time.",
    #     desired_tone="Analytical and thought-provoking",
    #     # Updated content focus to reflect the paired analysis of current and historical events
    #     content_focus="Each edition examines one significant current event and connects it to one relevant historical event, forming an evolving narrative.",
    #     # New field: specifying the primary content approach
    #     content_type="Event Pairing Analysis",
    #     # New field: specifying the newsletter's structure
    #     structure_type="Comparative Analysis",
    #     desired_length=LengthEnum.MEDIUM,
    #     preferred_writing_style="Concise, analytical, and engaging",
    #     # New field: recurring themes to maintain narrative continuity
    #     recurring_themes=["Historical parallels", "Lessons Revisited", "Evolving narratives"],
    #     generation_frequency=FrequencyEnum.MONTHLY,
    #     template=None,
    #     # Updated continuity to incorporate evolving narrative elements
    #     continuity="Over successive editions, thematic links are maintained by revisiting past comparisons and building on recurring lessons",
    #     past_newsletters=[
    #         PastNewsletter(
    #             newsletter_id="HELP-001",
    #             publication_date=datetime(2023, 10, 1, 9, 0, 0),
    #             title="Revisiting the Fall of Empires",
    #             summary="Explored the decline of ancient empires and drew parallels with modern geopolitical shifts.",
    #         ),
    #         PastNewsletter(
    #             newsletter_id="HELP-002",
    #             publication_date=datetime(2023, 11, 1, 9, 0, 0),
    #             title="Echoes of Revolution",
    #             summary="Compared revolutionary movements of the past with current protests, highlighting recurring patterns.",
    #         )
    #     ]
    # )
    return NewsletterMetadata(
    topic="Modern Academic Search Strategies",
    title="The Scholar's Compass",
    target_audience="Academics, researchers, and professionals eager to explore evolving search techniques in scholarly research.",
    newsletter_goal="To provide insightful analysis and practical tips on leveraging digital search innovations in academia.",
    desired_tone="Professional yet approachable, balancing depth with clarity.",
    content_focus="Exploration of innovative search methodologies and digital discovery platforms.",
    content_type="In-depth analysis and how-to guides",
    structure_type="Segmented layout with feature articles, comparative analyses, and expert tips",
    desired_length=LengthEnum.MEDIUM,
    preferred_writing_style="Clear, concise, and informative with an academic touch.",
    template="Introduction | Feature Article | Comparative Analysis | Expert Tips | Future Trends",
    recurring_themes=["Innovation in Research", "Digital Tools", "Search Strategies"],
    generation_frequency=FrequencyEnum.WEEKLY,
    continuity="Each edition builds on previous insights to track emerging trends and refine research strategies.",
    past_newsletters=[
        PastNewsletter(
            newsletter_id="NEWS-001",
            publication_date=datetime(2025, 1, 10, 9, 0),
            title="Unlocking New Possibilities in Digital Research",
            summary="An overview of breakthrough techniques reshaping the landscape of academic search."
        ),
        PastNewsletter(
            newsletter_id="NEWS-002",
            publication_date=datetime(2025, 1, 17, 9, 0),
            title="Refining Your Research Approach",
            summary="A deep dive into optimizing search strategies for comprehensive literature reviews."
        ),
        PastNewsletter(
            newsletter_id="NEWS-003",
            publication_date=datetime(2025, 1, 24, 9, 0),
            title="Charting the Future of Scholarly Discovery",
            summary="Insights into emerging trends and tools set to revolutionize academic research."
        )
    ]
)

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    number_of_queries: int = 2 # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    planner_provider: PlannerProvider = PlannerProvider.OPENAI # Defaults to OpenAI as provider
    planner_model: str = "o3-mini" # Defaults to OpenAI o3-mini as planner model
    writer_model: str = "claude-3-5-sonnet-latest" # Defaults to Anthropic as provider
    search_api: SearchAPI = SearchAPI.TAVILY # Default to TAVILY
    newsletter_metadata: NewsletterMetadata = field(default_factory=create_default_newsletter_metadata)

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})