from google.adk.agents import Agent
from ..shared_libraries import constants
from .prompt import DOCUMENT_PROCESSING_PROMPT
from .tools import get_tools

document_processing_agent = Agent(
    model=constants.MODEL,
    name="document_processing_agent",
    description="A specialist agent that can analyze PDFs, create new form fields using Azure AI, and fill them with data.",
    instruction=DOCUMENT_PROCESSING_PROMPT,
    tools=get_tools()
) 