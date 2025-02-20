from pydantic import BaseModel, Field, create_model
from typing import List, Optional, TypedDict, Annotated, Literal, TypeVar, Type, Any, get_type_hints, Union
from enum import Enum
import operator
import inspect
from functools import wraps
from typing import Callable, ParamSpec

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
        # Get all fields and their types
        fields = {}
        type_hints = get_type_hints(model_class)
        
        for field_name, field in model_class.model_fields.items():
            field_type = type_hints[field_name]
            
            # Handle Union types with potential shared first fields
            if SchemaAdapter._is_union_type(field_type):
                field_type = SchemaAdapter._create_discriminated_union(field_type, field_name)
            
            # Create new field without defaults
            fields[field_name] = (field_type, Field(description=field.description))
        
        # Create new model class
        return create_model(
            f"{prefix}{model_class.__name__}",
            __base__=BaseModel,
            **fields
        )
    
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
        openai_model_class = SchemaAdapter.create_openai_compatible_model(model.__class__)
        # Convert the instance, dropping any default values
        data = model.model_dump(exclude_defaults=True)
        return openai_model_class(**data).model_dump()
    
    @staticmethod
    def from_openai_schema(data: dict, model_class: Type[T]) -> T:
        """Convert OpenAI response data back to our internal model"""
        return model_class(**data)

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

class EffortLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ---------------------------------------------------------------------------
# Base Execution Item with dependency support
# ---------------------------------------------------------------------------
class ExecutionItemBase(BaseModel):
    id: str = Field(..., description="Unique identifier for this execution item")
    description: str = Field(..., description="Short description of the task")
    status: Status = Field(Status.PENDING, description="Current status of the item")
    output: Optional[str] = Field("", description="Resulting output after execution")
    dependencies: Optional[str] = Field("", description="What, if anything, the content of this item depends on")

# ---------------------------------------------------------------------------
# Research Execution Item
# ---------------------------------------------------------------------------
class ResearchItem(ExecutionItemBase):
    research_goal: str = Field(
        ...,
        description="The specific research goal. Use placeholders (e.g., {headlines}) if dependent on previous outputs."
    )
    # tools: Optional[List[str]] = Field(
    #     default_factory=list,
    #     description="List of tools or APIs to use for this research"
    # )
    effort: EffortLevel = Field(EffortLevel.MEDIUM, description="How intensive this research should be")
    important_context: Optional[str] = Field("", description="Important context or background information"
    )
    desired_output: str = Field(..., description="Expected format or nature of the research output"
    )

# ---------------------------------------------------------------------------
# Plan Reconsideration Execution Item
# ---------------------------------------------------------------------------
class PlanReconsiderationItem(ExecutionItemBase):
    reason: str = Field(
        ...,
        description="A forward-looking explanation as to why the plan should be reconsidered at this step. For example, 'Now that we expect to have the headlines, update further research steps.'"
    )
    guiding_questions: Optional[List[str]] = Field(
        default_factory=list,
        description="Questions to guide how the plan should be updated based on previous outputs"
    )
    proposed_changes: Optional[str] = Field(
        "", description="Summary of potential changes to the plan, to be updated after dependency resolution"
    )

# ---------------------------------------------------------------------------
# Template Builder Execution Item
# ---------------------------------------------------------------------------
class TemplateBuilderItem(ExecutionItemBase):
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
ExecutionItem = Union[ResearchItem, PlanReconsiderationItem, TemplateBuilderItem]

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
class NewsletterTemplate(BaseModel):
    title: str = Field(..., description="The title of the newsletter.")
    topic: str = Field(..., description="The main topic or focus of the newsletter.")
    summary: Optional[str] = Field(None, description="A brief summary or abstract of the newsletter.")
    sections: List[NewsletterSection] = Field(
        default_factory=list,
        description="The tree-like structure of newsletter sections."
    )
    desired_structure: Optional[str] = Field(
        None, description="A string describing the desired overall structure (if predefined)."
    )
    additional_context: Optional[str] = Field(
        None, description="Extra context or notes that might guide content generation."
    )

# Update state classes to use the new template types
class NewsletterStateInput(TypedDict):
    topic: str # Report topic
    
class NewsletterStateOutput(TypedDict):
    final_report: str # Final report

class NewsletterState(TypedDict):
    topic: str # Report topic    
    execution_plan: ExecutionPlan
    completed_items: Annotated[list, operator.add]
    template: NewsletterTemplate  # Updated to use NewsletterTemplate
    final_report: str # Final report

class ResearchBlockState(TypedDict):
    researchItem: ResearchItem
    search_queries: list[SearchQuery]
    source_str: str
    completed_items: list[ResearchItem]

class ResearchBlockOutputState(TypedDict):
    completed_items: list[ResearchItem] # Final key we duplicate in outer state for Send() API