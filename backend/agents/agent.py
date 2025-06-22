from google.adk.agents.llm_agent import Agent
from .shared_libraries import constants
from . import prompt
from .Bid_Discovery.agent import bid_discovery_manager
from .document_processing_agent.agent import document_processing_agent


root_agent = Agent(
    model=constants.MODEL,
    name="orchestrator_agent",
    description="The master orchestrator that delegates tasks to specialized manager agents.",
    instruction=prompt.ORCHESTRATOR_PROMPT,
    sub_agents=[
        bid_discovery_manager,
        document_processing_agent,
    ],
)
