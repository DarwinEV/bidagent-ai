from google.adk.agents.llm_agent import Agent
from ..shared_libraries import constants
from . import prompt
from . import tools

document_automation_manager = Agent(
    model=constants.MODEL,
    name="document_automation_manager",
    description="Manages the end-to-end process of document analysis, form field extraction, and PDF filling.",
    instruction=prompt.AUTOMATION_MANAGER_PROMPT,
    sub_agents=[], # This manager is fully in control and uses its own tools.
    tools=[
        # Primary Analysis Tools
        tools.extract_fields_with_local_heuristics,
        tools.analyze_document_with_docai,
        tools.run_ocr_and_extract_fields,
        
        # PDF Manipulation & Blueprint Tools
        tools.list_pdf_form_fields,
        tools.create_fields_from_blueprint,
        tools.fill_form_fields,
        
        # Utility & Debugging Tools
        tools.save_json_to_file,
        tools.check_configuration,
    ]
) 