# Change Log

## [2024-06-07] - Refactored PDF Tools for Robustness

### Objective
Resolve persistent save errors with certain PDF types by refactoring the PDF creation tools to be more atomic and reliable.

### Changes Made

1.  **Replaced Fragile Tools**:
    *   In `backend/agents/pdf_filler_manager/tools.py`, the `create_text_field` tool, which used a problematic incremental save, was removed.
    *   A new, more robust `create_and_fill_field` tool was introduced. This tool handles both field creation and filling in a single, atomic operation, always saving to a new output file to avoid corruption and encryption issues.

2.  **Simplified Agent Logic**:
    *   The `PDF_FILLER_PROMPT` was updated to use the new, simpler workflow. The agent no longer needs to chain separate `create` and `fill` calls, reducing complexity and potential for error.
    *   The agent's toolset in `agent.py` was updated to include the new `create_and_fill_field` tool and remove the old one.

### Expected Result
*   The `pdf_filler_manager` is now significantly more robust and should no longer fail on PDFs that are encrypted or have non-standard structures.
*   The agent's logic is simpler and more reliable.
*   The "save_inplace" and subsequent incremental save errors are resolved.

---

## [2024-06-07] - Patched PDF Field Creation Tool

### Objective
Fix the critical `AttributeError` in the `create_text_field` tool to enable the PDF creation workflow.

### Changes Made

1.  **Corrected Save Method**:
    *   In `backend/agents/pdf_filler_manager/tools.py`, the incorrect `doc.save_inplace()` method call was replaced with the correct `doc.save(pdf_path, incremental=True)`.

### Expected Result
*   The `pdf_filler_manager` can now successfully create and save new text fields on a PDF without crashing.
*   The stateful workflow, where the agent creates a field and then fills it, is now functional.
*   The `AttributeError: 'Document' object has no attribute 'save_inplace'` error is resolved.

---

## [2024-06-07] - Enhanced PDF Filler with Field Creation

### Objective
Upgrade the `pdf_filler_manager` to intelligently create new form fields on non-interactive PDFs, enabling it to handle a wider range of documents.

### Changes Made

1.  **Upgraded Tools (`tools.py`)**:
    *   Added `find_text_coordinates`: A new tool that can locate a specific string of text within a PDF and return its exact coordinates.
    *   Added `create_text_field`: A new tool that programmatically adds a new, empty text field to a PDF at a specified location.

2.  **Enhanced Agent Logic (`prompt.py`)**:
    *   The `PDF_FILLER_PROMPT` was completely rewritten with a new, branching workflow.
    *   The agent now first checks for existing fields. If none are found, it enters a "creation" mode.
    *   In creation mode, the agent uses the new tools to find text labels (e.g., "Company Name:"), create a new text field next to them, and then immediately fill that field with the user's data.

3.  **Updated Agent Definition (`agent.py`)**:
    *   The new `find_text_coordinates` and `create_text_field` tools were added to the `pdf_filler_manager`'s toolset, making them available for use.

### Expected Result
*   The `pdf_filler_manager` is no longer limited to pre-existing form fields.
*   It can now intelligently add and fill information on static, non-interactive PDF documents by finding text labels and creating fields on the fly.
*   This significantly increases the agent's utility and the range of documents it can successfully automate.

---

## [2024-06-07] - Implemented PDF Filler Manager

### Objective
Implement the `pdf_filler_manager` to provide the core functionality for automated document form filling.

### Changes Made

1.  **Added Dependency**:
    *   Added `PyMuPDF>=1.24.0` to `backend/requirements.txt` to enable PDF manipulation.

2.  **Created PDF Tools**:
    *   Created `backend/agents/pdf_filler_manager/tools.py` with two key functions:
        *   `list_pdf_form_fields`: To inspect a PDF and identify all fillable fields.
        *   `fill_pdf_form_field`: To write data to a specific field and save a new PDF.

3.  **Defined the Agent**:
    *   Created `backend/agents/pdf_filler_manager/prompt.py` with a detailed prompt outlining the form-filling workflow.
    *   Created `backend/agents/pdf_filler_manager/agent.py` to define the `pdf_filler_manager`, equipping it with the new tools and prompt.

4.  **Integrated into Orchestrator**:
    *   Imported and registered the `pdf_filler_manager` as a sub-agent within the main `root_agent` in `backend/agents/agent.py`.

### Expected Result
*   The platform now has a functional manager capable of receiving user data and a PDF, identifying form fields, and programmatically filling them out.
*   The `root_agent` can now successfully delegate form-filling tasks to this new, specialized manager.
*   The system is prepared for Phase 4: UI Integration.

---

## [2024-06-07] - Agent Naming Convention and ADK Compliance

### Objective
Resolve critical framework errors by aligning agent naming conventions with `google-adk` expectations and eliminating import conflicts.

### Changes Made

1.  **Resolved Module Not Found Error**:
    *   Created `backend/agents/__init__.py` to ensure the `agents` directory is treated as a Python package, allowing the ADK framework to correctly locate and load the main agent module.

2.  **Complied with ADK `root_agent` Convention**:
    *   Renamed the main `orchestrator_agent` variable to `root_agent` in `backend/agents/agent.py`. This aligns with the default entry-point variable name expected by the ADK.

3.  **Resolved Naming Conflict**:
    *   Renamed the agent in `backend/agents/Bid_Discovery/sub_agents/rag_agent/agent.py` from `root_agent` to `rag_agent`.
    *   Updated the corresponding import in the `bid_discovery_manager` to use the new, unambiguous name.

### Expected Result
*   The application is now free of startup errors related to module loading and agent naming.
*   The agent hierarchy is clear: `root_agent` is the top-level orchestrator, and all sub-agents have unique, descriptive names, preventing future import conflicts.

---

## [2024-06-07] - Hierarchical Agent Architecture Refactoring

### Objective
Restructure the agent system to a scalable, hierarchical model with a clear separation of concerns, and establish a truly shared library for common code.

### Changes Made

1.  **Established Top-Level Orchestrator**:
    *   Created `backend/agents/agent.py` to act as the main orchestrator agent, responsible for delegating tasks to specialized managers.
    *   Created `backend/agents/prompt.py` to house the orchestrator's high-level prompt.

2.  **Created `bid_discovery_manager`**:
    *   The existing agent in `backend/agents/Bid_Discovery/` was formally converted into a specialized manager.
    *   The agent was renamed to `bid_discovery_manager` within its definition file.

3.  **Centralized `shared_libraries`**:
    *   Moved the `shared_libraries` directory from `backend/agents/Bid_Discovery/` to `backend/agents/`.
    *   Updated the import paths in all dependent files (`orchestrator_agent`, `bid_discovery_manager`, and its sub-agents) to reflect the new, centralized location.

4.  **Placeholder for Future Work**:
    *   Created an empty `backend/agents/pdf_filler_manager/` directory to prepare for the next phase of development.

### Expected Result
*   A clean, hierarchical agent structure that is easier to understand, maintain, and extend.
*   A main `orchestrator_agent` at `backend/agents/agent.py` that directs all user interaction.
*   A centralized `shared_libraries` folder accessible to all current and future agents, preventing code duplication.

---

## [2025-06-06] - Intelligent Search Query Enhancement

### Objective
Empower the `bid_search_agent` to intelligently expand and refine a user's search query to yield more relevant bid opportunities.

### Changes Made

1.  **Modified `backend/agents/Bid_Discovery/sub_agents/search_results/prompt.py`**:
    *   Added a new `<Intelligent_Query_Refinement>` section to the `SEARCH_RESULT_AGENT_PROMPT`.
    *   This instructs the agent to use its LLM knowledge to expand user-provided keywords with synonyms, related technical terms, and relevant classification codes before initiating a search.
    *   The agent will now autonomously use an enriched set of keywords to perform a more effective search without requiring user confirmation.

### Expected Result
*   The `bid_search_agent` will find more relevant bids by searching for a broader, more professional set of terms, even if the user provides simple or non-expert keywords.
*   The overall quality and relevance of the bid discovery results will be significantly improved, providing more value to the user.

---

## [2025-06-05] - Delayed WebDriver Initialization

### Objective
Prevent the browser tab from opening prematurely when the application starts.

### Changes Made

1.  **Modified `backend/agents/Bid_Discovery/sub_agents/search_results/agent.py`**:
    *   Removed the immediate initialization of the Selenium WebDriver.
    *   Introduced a `get_driver()` function that initializes a singleton WebDriver instance on its first call.
    *   Updated all browser-related tool functions (`go_to_url`, `take_screenshot`, etc.) to use the `get_driver()` function.

### Expected Result
*   The Selenium WebDriver and the browser tab will only be launched when the `bid_search_agent` needs to perform a web-related action, not on application startup.
*   This improves resource management and provides a better user experience.

---

## [2025-06-05] - Agent Interaction Refactoring

### Objective
Refactor the agent interaction flow to eliminate redundant information gathering and clarify agent roles.

### Changes Made

1.  **Modified `backend/agents/Bid_Discovery/prompt.py`**:
    *   Updated the `ROOT_PROMPT` for the main Bid Discovery agent.
    *   The agent now acts as a high-level router, asking the user to choose between "Bid Discovery" and "Document Analysis."
    *   Removed all specific questions about keywords, portals, and NAICS codes from this prompt.

2.  **Modified `backend/agents/Bid_Discovery/agent.py`**:
    *   Renamed the imported RAG agent from `root_agent` to `rag_agent` to prevent naming confusion with the main `root_agent`.
    *   Updated the `sub_agents` list to reflect this change.

### Expected Result
*   The user experience is streamlined. The user is no longer asked the same questions by multiple agents.
*   The main "manager" agent correctly delegates tasks to the appropriate sub-agent (`bid_search_agent` or `rag_agent`).
*   The `bid_search_agent` is now solely responsible for gathering bid discovery details (keywords, portals, etc.) from the user and initiating the web search, ensuring the browser tab is opened only after collecting the necessary information.
*   Code readability is improved by renaming the RAG agent.

## [2024-06-10] - Iterative Debugging & Heuristic Enhancement

### Objective
Systematically identify and resolve a series of cascading errors in the document automation workflow, including library compatibility issues, file path errors, and logical flaws, while iteratively improving the precision of the form field extraction tools based on user feedback.

### Changes Made

1.  **Fixed Library Incompatibility (`AttributeError`)**:
    *   Identified that the `fitz.TextWidget` class was not available in the installed version of `PyMuPDF`.
    *   Refactored the `create_fields_from_blueprint` tool in `document_automation_manager/tools.py` to use the older, more compatible `fitz.Widget` method, ensuring the code works without requiring a library upgrade.

2.  **Repaired File Path Logic (`TypeError`)**:
    *   Diagnosed that a `TypeError` was caused by a faulty `get_output_path` utility function that was missing a required `clean_base_name` parameter.
    *   Corrected the function signature in `shared_libraries/utils.py` to restore the missing parameter, fixing the toolchain for saving the final, filled PDF.

3.  **Enhanced Local Heuristic Tool for Precision**:
    *   Based on user feedback that the tool was only finding "about half" of the fields, the `extract_fields_with_local_heuristics` tool was significantly upgraded.
    *   The tool's logic was expanded from a simple underline-finder to a multi-strategy system that also identifies fields based on colon-terminated labels (e.g., "Name:"). This dramatically improved its coverage and accuracy.

4.  **Reinforced Agent Error Handling**:
    *   The `AUTOMATION_MANAGER_PROMPT` was updated with explicit `If-Then` logic, commanding the agent to **STOP** and report the exact error if a critical tool like `create_fields_from_blueprint` fails. This prevents the agent from getting stuck in failure loops or hallucinating successful outcomes.

### Expected Result
*   The document automation workflow is now significantly more robust and resilient.
*   The agent can correctly create and fill PDFs without crashing due to library or file path errors.
*   The local heuristic tool is more accurate and captures a higher percentage of form fields.
*   The agent's error handling is more predictable and transparent to the user.

---

# modify the phrase with words that will produce better results as well as try other words if we do not get good results.
# Find a way for it to look for procurement links.