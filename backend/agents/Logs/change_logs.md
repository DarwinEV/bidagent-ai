# Change Log

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

# modify the phrase with words that will produce better results as well as try other words if we do not get good results.
# Find a way for it to look for procurement links.