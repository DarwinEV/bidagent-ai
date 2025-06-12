from google.adk.agents.llm_agent import Agent
from ....shared_libraries import constants
from . import prompt
from pydantic import BaseModel, Field
from typing import List, Optional

class FormField(BaseModel):
    """Represents a single identified form field in the document."""
    field_name: str = Field(description="The cleaned-up name for the form field.")
    field_type: str = Field(description="The inferred HTML input type (e.g., 'text', 'date', 'email').")
    placeholder_text: Optional[str] = Field(None, description="Example text or format for the field.")
    is_required: bool = Field(description="True if the field is likely mandatory, otherwise False.")
    confidence_score: float = Field(description="A score from 0.0 to 1.0 indicating confidence in the extraction.")
    context_snippet: str = Field(description="A snippet of original text for user verification.")
    coordinates: Optional[List[dict]] = Field(None, description="A list of x, y vertices for the field's bounding box.")

class FormFieldList(BaseModel):
    """A container for a list of identified form fields."""
    form_fields: List[FormField]

json_formatter_agent = Agent(
    model=constants.MODEL,
    name="json_formatter_agent",
    description="Takes raw JSON from a tool and formats it into a structured list of form fields.",
    instruction=prompt.JSON_FORMATTER_PROMPT,
    output_schema=FormFieldList,
) 