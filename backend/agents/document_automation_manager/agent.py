from google.adk.agents.llm_agent import Agent
from ..shared_libraries import constants
from . import prompt
from . import tools
from .sub_agents.docai_tool_agent.agent import docai_tool_agent
from .sub_agents.ocr_tool_agent.agent import ocr_tool_agent
from .sub_agents.json_formatter_agent.agent import json_formatter_agent
from .sub_agents.pdf_filler_agent.agent import pdf_filler_agent

document_automation_manager = Agent(
    model=constants.MODEL,
    name="document_automation_manager",
    description="Manages the process of analyzing a document to extract a structured list of form fields based on a specified mode.",
    instruction=prompt.AUTOMATION_MANAGER_PROMPT,
    sub_agents=[
        docai_tool_agent,
        ocr_tool_agent,
        json_formatter_agent,
        pdf_filler_agent,
    ],
    tools=[
        tools.save_json_to_file,
    ]
) 