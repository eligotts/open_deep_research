from pydantic import BaseModel, Field, create_model
from typing import List, Optional, TypedDict, Annotated, Literal, TypeVar, Type, Any, get_type_hints, Union, Annotated, Sequence
from enum import Enum
import operator
import inspect
from functools import wraps
from typing import Callable, ParamSpec
from datetime import datetime
from langchain_core.messages import BaseMessage


T = TypeVar('T', bound=BaseModel)
P = ParamSpec('P')
R = TypeVar('R', bound=BaseModel)

class SchemaAdapter:
    """Adapter class to convert between internal Pydantic models and OpenAI-compatible models"""
    
    @staticmethod
    def create_openai_compatible_model(model_class: Type[T], prefix: str = "OpenAI") -> Type[BaseModel]:
        """
        Creates an OpenAI-compatible version of a Pydantic model by:
        1. Removing default values
        2. Handling union types with shared first fields
        """
        print(f"\nCreating OpenAI compatible model for {model_class.__name__}")
        # Get all fields and their types
        fields = {}
        type_hints = get_type_hints(model_class)
        
        for field_name, field in model_class.model_fields.items():
            field_type = type_hints[field_name]
            print(f"Processing field {field_name}: {field_type}")
            
            # Handle Union types with potential shared first fields
            if SchemaAdapter._is_union_type(field_type):
                print(f"Found Union type in {field_name}")
                field_type = SchemaAdapter._create_discriminated_union(field_type, field_name)
                print(f"Discriminated union created: {field_type}")
            
            # Create new field without defaults
            fields[field_name] = (field_type, Field(description=field.description))
        
        # Create new model class
        new_model = create_model(
            f"{prefix}{model_class.__name__}",
            __base__=BaseModel,
            **fields
        )
        print(f"Created new model: {new_model.__name__} with fields: {list(fields.keys())}")
        return new_model
    
    @staticmethod
    def _is_union_type(type_hint: Any) -> bool:
        """Check if a type hint is a Union type"""
        return hasattr(type_hint, "__origin__") and type_hint.__origin__ is Union
    
    @staticmethod
    def _create_discriminated_union(union_type: Any, field_name: str) -> Any:
        """
        Creates a discriminated union type by adding a type discriminator
        if the union members share first fields
        """
        union_args = union_type.__args__
        
        # Check if we need to add discriminators
        first_fields = SchemaAdapter._get_first_fields(union_args)
        if len(set(first_fields)) != len(first_fields):
            # Create new discriminated versions of the union members
            new_args = []
            for i, arg in enumerate(union_args):
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    # Add discriminator field as the first field
                    discriminator = f"type_{field_name}_{i}"
                    new_arg = create_model(
                        f"Discriminated{arg.__name__}",
                        __base__=BaseModel,
                        type=(Literal[discriminator], Field(...)),
                        **{k: (v, Field(...)) for k, v in get_type_hints(arg).items()}
                    )
                    new_args.append(new_arg)
                else:
                    new_args.append(arg)
            return Union[tuple(new_args)]
        return union_type
    
    @staticmethod
    def _get_first_fields(types: tuple) -> list[str]:
        """Get the names of the first fields for each type in a union"""
        first_fields = []
        for t in types:
            if inspect.isclass(t) and issubclass(t, BaseModel):
                fields = list(t.model_fields.keys())
                first_fields.append(fields[0] if fields else None)
            else:
                first_fields.append(None)
        return first_fields
    
    @staticmethod
    def to_openai_schema(model: T) -> dict:
        """Convert a model instance to an OpenAI-compatible schema"""
        print(f"\nConverting {type(model).__name__} to OpenAI schema")
        openai_model_class = SchemaAdapter.create_openai_compatible_model(model.__class__)
        # Convert the instance, dropping any default values
        data = model.model_dump(exclude_defaults=True)
        print(f"Model data without defaults: {data}")
        result = openai_model_class(**data).model_dump()
        print(f"Final OpenAI schema: {result}")
        return result
    
    @staticmethod
    def from_openai_schema(data: dict, model_class: Type[T]) -> T:
        """Convert OpenAI response data back to our internal model"""
        print(f"\nConverting OpenAI response back to {model_class.__name__}")
        print(f"Input data: {data}")
        result = model_class(**data)
        print(f"Converted to internal model with defaults: {result.model_dump()}")
        return result

def openai_compatible(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to make a function that returns a Pydantic model OpenAI-compatible
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Get the return type annotation
        return_type = get_type_hints(func).get('return')
        if not return_type or not issubclass(return_type, BaseModel):
            raise ValueError("Function must return a Pydantic model")
        
        # Create OpenAI-compatible model
        openai_model = SchemaAdapter.create_openai_compatible_model(return_type)
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # Convert to OpenAI schema and back to ensure compatibility
        openai_data = SchemaAdapter.to_openai_schema(result)
        return SchemaAdapter.from_openai_schema(openai_data, return_type)
    
    return wrapper

# ---------------------------------------------------------------------------
# Enums for status and effort indications
# ---------------------------------------------------------------------------
class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# class EffortLevel(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

class BlockType(str, Enum):
    RESEARCH = "research"
    RECONSIDERATION = "reconsideration"
    TEMPLATE_BUILDING = "template_building"

# ---------------------------------------------------------------------------
# Base Execution Item with dependency support
# ---------------------------------------------------------------------------
class ExecutionBlock(BaseModel):
    id: str = Field(..., description="Unique identifier for this execution block")
    block_type: BlockType = Field(..., description="Type of block (research, reconsideration, template_building)")
    description: str = Field(..., description="Short description of the block's purpose")
    status: Status = Field(Status.PENDING, description="Current status of the block")
    output: Optional[str] = Field("", description="Output generated from this block")

class ResearchBlock(ExecutionBlock):
    research_goal: str = Field(..., description="The specific research objective for this block")
    desired_output: str = Field(..., description="The expected format or content of the research output")
    relevant_context: str = Field(..., description="Any relevant context for the block of research")
    evaluation_criteria: Optional[str] = Field(
        "",
        description="Criteria to assess the research output"
    )

class ReconsiderationBlock(ExecutionBlock):
    reason: str = Field(..., description="Explanation for why reconsideration is needed at this point")
    guiding_questions: List[str] = Field(
        default_factory=list,
        description="Questions to help guide how the plan should be updated based on previous outputs"
    )
    proposed_changes: Optional[str] = Field(
        "",
        description="Summary of potential changes after re-evaluation"
    )


# ---------------------------------------------------------------------------
# Template Builder Execution Item
# ---------------------------------------------------------------------------
class TemplateBuilderItem(ExecutionBlock):
    template_goal: str = Field(
        ...,
        description="The goal for constructing or updating the newsletter template"
    )
    constraints: Optional[str] = Field(
        "", description="Any constraints or formatting rules that should be followed"
    )
    notes: Optional[str] = Field(
        "", description="Additional notes for building the template"
    )

# ---------------------------------------------------------------------------
# Union of all Execution Items for the plan
# ---------------------------------------------------------------------------
ExecutionItem = Union[ResearchBlock, ReconsiderationBlock, TemplateBuilderItem]

# ---------------------------------------------------------------------------
# Overall Execution Plan Model
# ---------------------------------------------------------------------------
class ExecutionPlan(BaseModel):
    items: List[ExecutionItem] = Field(
        ..., description="Ordered list of execution items for the newsletter generation process"
    )

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )

class Feedback(BaseModel):
    grade: Literal["pass","fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )

# ---------------------------------------------------------------------------
# Enum to track the level of detail for each section
# ---------------------------------------------------------------------------
class SectionDetailLevel(str, Enum):
    IDEA = "idea"         # Basic idea/placeholder
    PARTIAL = "partial"   # Some research/template in place
    COMPLETE = "complete" # Final content is ready

# ---------------------------------------------------------------------------
# Model for a section of the final newsletter
# ---------------------------------------------------------------------------
class NewsletterSection(BaseModel):
    name: str = Field(..., description="The title of the section (e.g., 'Introduction', 'Analysis').")
    definition: str = Field(..., description="A brief explanation of what this section should cover.")
    template: Optional[str] = Field(
        None, description="Optional instructions or formatting guidelines for the section's final output."
    )
    output: Optional[str] = Field(
        None, description="The final written content of the section (populated when complete)."
    )
    detail_level: SectionDetailLevel = Field(
        SectionDetailLevel.IDEA,
        description="Indicates the current state of the section: idea, partial, or complete."
    )
    dependencies: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "Notes about dependencies on other sections. For example, 'Depends on the output of the Research section on AI headlines.'"
        )
    )
    children: List["NewsletterSection"] = Field(
        default_factory=list,
        description="Child sections or subsections, enabling a nested newsletter structure."
    )

# Allow recursive models
NewsletterSection.model_rebuild()

# ---------------------------------------------------------------------------
# Overall Newsletter Template Model
# ---------------------------------------------------------------------------
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


class NewsletterTemplate(BaseModel):
    sections: List[NewsletterSection] = Field(
        default_factory=list,
        description="The tree-like structure of newsletter sections."
    )


# Update state classes to use the new template types
class NewsletterStateInput(TypedDict):
    newsletter_metadata: Optional[NewsletterMetadata]
    
class NewsletterStateOutput(TypedDict):
    final_report: str # Final report

class NewsletterState(TypedDict):
    newsletter_metadata: NewsletterMetadata 
    execution_plan: ExecutionPlan
    initial_execution_plan: str
    completed_items: Annotated[list, operator.add]
    template: NewsletterTemplate  # Updated to use NewsletterTemplate
    final_report: str # Final report

class ResearchBlockState(TypedDict):
    researchItem: ResearchBlock
    search_queries: list[SearchQuery]
    source_str: str
    completed_items: list[ResearchBlock]

    # might only need these
    messages: Annotated[Sequence[BaseMessage], operator.add]

class ResearchBlockOutputState(TypedDict):
    completed_items: list[ResearchBlock] # Final key we duplicate in outer state for Send() API