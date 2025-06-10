# Update 2: Intelligent Search Query Enhancement

## 1. Objective
To empower the `bid_search_agent` to intelligently expand and refine a user's search query. Instead of using the user's exact words, the agent will leverage its LLM capabilities to generate better search terms, leading to more relevant and comprehensive bid discoveries.

## 2. Analysis of the Problem
The current search agent takes user-provided keywords, industry, or region at face value. A user might not be an expert in procurement terminology and could use words that yield poor search results (e.g., "computer work" instead of "IT services"). This limits the effectiveness of the bid discovery process.

## 3. Proposed Solution - Step-by-Step

### Step 1: Modify the Search Agent's Prompt (`SEARCH_RESULT_AGENT_PROMPT`)
**File:** `backend/agents/Bid_Discovery/sub_agents/search_results/prompt.py`

**Action:** I will update the `SEARCH_RESULT_AGENT_PROMPT` to include a new instruction block for "Intelligent Query Refinement." This will guide the agent to think about and improve the user's search terms before executing the search.

**New Prompt Logic to be Added:**
I will insert a new section into the prompt, likely before the `<Navigation & Searching>` step.

```
<Intelligent_Query_Refinement>
- Before searching, take a moment to analyze the user-provided keywords, industry, and region.
- Use your expert knowledge of procurement and various industries to expand these terms. Generate a list of synonyms, related technical terms, and relevant classification codes (like NAICS or UNSPSC) that are likely to produce better search results.
- For example, if a user asks for bids related to "computer work," you should automatically expand your search to include terms like "IT services," "network administration," "cybersecurity," "software development," and "data management."
- You should not ask the user for confirmation. Autonomously use this new, enriched set of keywords to perform a more effective search.
- Your goal is to act as an expert assistant who knows how to find the best opportunities, even if the user doesn't know the exact terms to use.
</Intelligent_Query_Refinement>
```

The existing `<Navigation & Searching>` step will then be updated to use the terms generated from this new step.

### Step 2: Update Change Log
**File:** `backend/agents/Logs/change_logs.md`

**Action:** After successfully implementing the prompt enhancement, I will document the changes in the change log, creating a new entry for this feature.

## 4. Expected Outcome
- The `bid_search_agent` will no longer be limited to the user's exact phrasing.
- The agent will automatically find more relevant bids by searching for a wider, more professional set of terms.
- The user will get better results without needing to be an expert in search-term optimization.
- The overall value of the Bid Discovery feature will be significantly increased. 

# Bid Agent System Refactoring Plan

## 1. Objective
Refactor the agent interaction flow to eliminate redundant information gathering. The "Manager" agent should act as a high-level router, directing users to specialized sub-agents (Search or RAG) without collecting detailed task-specific information itself. The Search agent should be solely responsible for gathering all necessary details for bid discovery and performing the web search.

## 2. Analysis of the Problem
The current implementation has both the main Bid Discovery agent (`backend/agents/Bid_Discovery/agent.py` via `prompt.ROOT_PROMPT`) and the Search agent (`backend/agents/Bid_Discovery/sub_agents/search_results/agent.py` via `prompt.SEARCH_RESULT_AGENT_PROMPT`) asking the user for the same information (procurement portal, keywords, etc.). The main agent also initiates web navigation, which should be the responsibility of the search agent.

This leads to a poor user experience where the user has to provide the same information twice.

## 3. Proposed Solution - Step-by-Step

### Step 1: Modify the Main Agent's Prompt (`ROOT_PROMPT`)
**File:** `backend/agents/Bid_Discovery/prompt.py`

**Action:** Update `ROOT_PROMPT` to remove detailed questions. The agent should only ask the user to choose between "Bid Discovery" and "Document Analysis".

**Current `ROOT_PROMPT`:**
- Asks for keywords, NAICS codes, portal, etc.
- Explicitly calls `bid_search_agent` with parameters.

**New `ROOT_PROMPT`:**
```python
"""
You are a master Bid Strategist agent. Your role is to understand the user's goal and delegate to the appropriate sub-agent.

You have two primary functions available to you:
1.  **Bid Discovery**: Find new bid opportunities on procurement websites.
2.  **Document Analysis**: Analyze an existing bid document to extract key information and answer questions.

Your Steps:
1. Greet the user and ask which of these two functions they would like to perform.
2. If the user chooses "Bid Discovery", delegate the entire task to the `bid_search_agent`.
3. If the user chooses "Document Analysis", delegate the task to the `rag_agent`.
4. Let the selected sub-agent handle all further interaction for their task. Do not ask for any details like keywords or websites yourself.
"""
```

### Step 2: Verify the Search Agent's Prompt (`SEARCH_RESULT_AGENT_PROMPT`)
**File:** `backend/agents/Bid_Discovery/sub_agents/search_results/prompt.py`

**Action:** Ensure the `SEARCH_RESULT_AGENT_PROMPT` is comprehensive and handles the full interaction for bid discovery. This prompt is already well-defined for this purpose and likely needs no major changes. It correctly asks for the portal, keywords, and other details. It also has access to web navigation tools, so it can open the browser tab at the correct time (after gathering information).

### Step 3: Improve Clarity in the Main Agent Definition
**File:** `backend/agents/Bid_Discovery/agent.py`

**Action:** Rename the imported RAG agent to avoid confusion.

**Current Code:**
```python
# ...
from .sub_agents.rag_agent.agent import root_agent

root_agent = Agent(
    # ...
    sub_agents=[
        bid_search_agent,
        root_agent
    ],
)
```

**New Code:**
```python
# ...
from .sub_agents.rag_agent.agent import root_agent as rag_agent

root_agent = Agent(
    # ...
    sub_agents=[
        bid_search_agent,
        rag_agent
    ],
)
```

## 4. Expected Outcome
- The main agent will first ask the user whether they want to "discover bids" or "analyze a document".
- If the user chooses "discover bids", the `bid_search_agent` will be invoked.
- The `bid_search_agent` will then ask for the website, keywords, etc.
- After collecting the information, the `bid_search_agent` will use its tools to open a browser tab and perform the search.
- The user will no longer be asked for the same information multiple times.
- The responsibility of each agent will be clearly separated.


