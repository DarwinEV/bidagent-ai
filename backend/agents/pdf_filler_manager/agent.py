from google.adk.agents.llm_agent import Agent
from ..shared_libraries import constants
from . import prompt
from . import tools

pdf_filler_manager = Agent(
    model=constants.MODEL,
    name="pdf_filler_manager",
    description="Manages the process of filling out PDF forms by analyzing documents and user-provided data.",
    instruction=prompt.PDF_FILLER_PROMPT,
    tools=[
        tools.list_pdf_form_fields,
        tools.fill_pdf_form_field,
    ],
) 