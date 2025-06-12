from google.adk.agents.llm_agent import Agent
from ....shared_libraries import constants
from . import tools

docai_tool_agent = Agent(
    model=constants.MODEL,
    name="docai_tool_agent",
    description="A simple agent that provides the tool to analyze a document with Google Document AI's Form Parser.",
    tools=[
        tools.analyze_document_with_docai,
    ],
) 