from google.adk.agents.llm_agent import Agent
from ....shared_libraries import constants
from . import tools

pdf_filler_agent = Agent(
    model=constants.MODEL,
    name="pdf_filler_agent",
    description="An agent equipped with tools to first create empty fields on a PDF and then fill them with user data.",
    tools=[
        tools.create_fields_from_blueprint,
        tools.fill_form_fields,
    ],
) 