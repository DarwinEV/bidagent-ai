# Change Log

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