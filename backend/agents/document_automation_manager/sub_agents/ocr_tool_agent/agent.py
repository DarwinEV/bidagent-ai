from google.adk.agents.llm_agent import Agent
from ....shared_libraries import constants
from . import tools

ocr_tool_agent = Agent(
    model=constants.MODEL,
    name="ocr_tool_agent",
    description="An agent that uses OCR to extract all words and their precise coordinates from a document.",
    tools=[
        tools.get_document_text_with_coordinates,
    ],
) 