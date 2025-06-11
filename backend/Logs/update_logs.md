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


=======
# Master Executable Plan

This document provides a detailed, step-by-step implementation plan for each phase outlined in the project's master plan.

---

## Phase 1: Core Agent Refactoring & Optimization (Executable Plan)

### Objective:
Streamline the agent interaction flow, improve user experience, and optimize resource usage.

#### **Step 1.1: Refactor Main Agent into a High-Level Router**
-   **Action:** Modify the root agent's prompt (`backend/agents/Bid_Discovery/prompt.py`) to remove task-specific questions (e.g., for keywords, portals). The prompt should only ask the user to choose between high-level functions like "Bid Discovery" or "Document Analysis."
-   **Action:** Ensure the agent's logic delegates the entire conversation to the appropriate sub-agent based on the user's choice.

#### **Step 1.2: Implement Lazy Loading for WebDriver**
-   **Action:** In the `search_results` agent (`.../search_results/agent.py`), refactor the Selenium WebDriver initialization.
-   **Action:** Remove the global WebDriver instantiation. Create a `get_driver()` function that initializes the driver as a singleton on its first call.
-   **Action:** Update all browser-related tools (`go_to_url`, `take_screenshot`, etc.) to call `get_driver()` before executing browser commands.

#### **Step 1.3: Enhance Search Agent Intelligence**
-   **Action:** Modify the search agent's prompt (`.../search_results/prompt.py`).
-   **Action:** Add a new instruction step, `<Intelligent_Query_Refinement>`, before the search execution step. This new step commands the agent to use its own knowledge to expand the user's keywords with synonyms and related professional terms.

---

## Phase 2: Hierarchical Agent Architecture (Executable Plan)

### Objective:
Restructure the agent system into a clear hierarchy with a main orchestrator and specialized managers.

#### **Step 2.1: Establish the Top-Level Orchestrator (`root_agent`)**
-   **Action:** Create a main `agent.py` file directly inside `backend/agents/`.
-   **Action:** Define the primary agent in this file and name the variable `root_agent` to comply with `google-adk` framework conventions.
-   **Action:** Create a corresponding `prompt.py` to instruct the `root_agent` to delegate tasks to its specialized manager sub-agents.

#### **Step 2.2: Formalize the `bid_discovery_manager`**
-   **Action:** Convert the existing `Bid_Discovery` agent into a formal manager.
-   **Action:** Rename the agent variable within `backend/agents/Bid_Discovery/agent.py` to `bid_discovery_manager` to reflect its role.

#### **Step 2.3: Centralize Shared Libraries**
-   **Action:** Move the `shared_libraries` directory from its nested location to the top-level `backend/agents/` directory.
-   **Action:** Update all `import` statements in the `root_agent`, `bid_discovery_manager`, and its sub-agents to use the new, corrected relative paths (e.g., `from ..shared_libraries import constants`).

#### **Step 2.4: Ensure Python Packging**
-   **Action:** Create an `__init__.py` file in `backend/agents/` to ensure the directory is treated as a Python package, resolving module loading errors.

---

## Phase 3: PDF Form Filling & Document Automation (Executable Plan)

### Objective:
Introduce document automation capabilities, allowing the system to programmatically create and complete bid forms, even on non-interactive PDFs.

#### **Step 3.1: Add `PyMuPDF` Dependency**
-   **Action:** Add the `PyMuPDF` library to the `backend/requirements.txt` file to enable advanced PDF manipulation.

#### **Step 3.2: Create PDF Manipulation Tools**
-   **Action:** In a new `tools.py` file within `backend/agents/pdf_filler_manager/`, create the necessary functions:
    -   `list_pdf_form_fields(pdf_path)`: To inspect a PDF and find existing form fields.
    -   `find_text_coordinates(pdf_path, text_to_find)`: To find the exact coordinates of a given string on a PDF page.
    -   `create_text_field(pdf_path, ...)`: To programmatically add a new, writable text field to the PDF at specified coordinates.
    -   `fill_pdf_form_field(pdf_path, field_name, value)`: To write data into a field (either existing or newly created).

#### **Step 3.3: Implement the `pdf_filler_manager`**
-   **Action:** Create the `agent.py` and `prompt.py` for the manager inside `backend/agents/pdf_filler_manager/`.
-   **Action:** The prompt must define a branching workflow: If existing fields are found, fill them. If not, use the creation tools to find text labels, create new fields, and then fill them.
-   **Action:** The agent definition must be equipped with all the new PDF tools.

#### **Step 3.4: Integrate the Manager**
-   **Action:** In the main `root_agent` (`backend/agents/agent.py`), import the newly created `pdf_filler_manager` and add it to the `sub_agents` list, making it available for delegation.

---

## Phase 4: UI Integration for Document Automation (Executable Plan)

### Objective:
Provide a seamless frontend user experience for the new PDF filling functionality.

#### **Step 4.1: Create Backend API for File Handling**
-   **Action:** Create a new file, `backend/routes/pdf_routes.py`.
-   **Action:** In this file, define two Flask routes:
    -   **`POST /api/upload-pdf`**: This endpoint will receive a file from the frontend. It will save the file to a secure, temporary directory on the server (e.g., `/tmp/uploads/`) and return the server-side file path as a JSON response (e.g., `{"filePath": "/tmp/uploads/document.pdf"}`).
    -   **`GET /api/download-pdf/<filename>`**: This endpoint will allow the user to download a completed file. It will use Flask's `send_from_directory` to securely serve the file from the temporary directory where filled PDFs are saved.
-   **Action:** Register this new route blueprint in the main Flask `app.py`.

#### **Step 4.2: Develop Frontend UI Components**
-   **Action:** In your frontend application, create a new view or page for "PDF Form Filling."
-   **Action:** Implement a **File Uploader** component. When a user selects a PDF, the component will make a `POST` request to the `/api/upload-pdf` endpoint and store the returned `filePath` in the component's state.
-   **Action:** Implement a **Company Information Form**. This will be a standard web form with input fields for "Company Name," "Address," "EIN," etc.
-   **Action:** Implement a **"Fill Document" Button**. When clicked, this button will trigger the main agent interaction. It will send a message to the `root_agent` that includes:
    -   The user's intent (e.g., "I want to fill a PDF").
    -   The `filePath` obtained from the uploader.
    -   All the data collected from the company information form.
-   **Action:** Implement a **Status and Download** area. After the agent interaction is complete, the final response should contain the path to the new, filled document. The UI will display this and present a "Download Filled PDF" link that points to the `/api/download-pdf/<filename>` endpoint.

# Update 5: PDF Tool Bug Fix

## 1. Objective
Fix the `AttributeError: 'Document' object has no attribute 'save_inplace'` error that occurs when the `pdf_filler_manager` attempts to create a new form field. This will make the PDF creation workflow functional.

## 2. Analysis of the Error
The error is caused by an incorrect method call in the `create_text_field` tool within `backend/agents/pdf_filler_manager/tools.py`. The method `doc.save_inplace()` does not exist in the PyMuPDF library. The correct method to save changes to the same file is `doc.save(pdf_path, incremental=True)`. This allows for a stateful workflow where one tool can create a field and a subsequent tool can fill it within the same PDF file.

## 3. Execution Plan

### **Step 1: Correct the `create_text_field` Tool**
-   **File to Modify:** `backend/agents/pdf_filler_manager/tools.py`
-   **Action:** Locate the `create_text_field` function.
-   **Change:** Replace the line `doc.save_inplace()` with `doc.save(pdf_path, incremental=True)`. This will correctly save the newly created field to the PDF file, allowing the `fill_pdf_form_field` tool to find and populate it in the next step.

# Update 6: Robust PDF Tool Refactoring

## 1. Objective
Fix the workflow-halting error caused by `incremental` saves failing on certain PDFs. This will be achieved by refactoring the PDF tools to be more atomic and robust, ensuring they can handle a wider variety of document types, including those with encryption or non-standard structures.

## 2. Analysis of the Error
The agent's output shows that `doc.save(pdf_path, incremental=True)` is failing. This suggests that appending changes is not a universally reliable method. The current workflow, which relies on one tool creating a field and a second tool filling it, is fragile. A better approach is to combine these actions into a single, atomic tool that always produces a new, clean output file.

## 3. Execution Plan

### **Step 1: Refactor the PDF Tools (`tools.py`)**
-   **File to Modify:** `backend/agents/pdf_filler_manager/tools.py`
-   **Action 1: Remove `create_text_field`**: This tool and its problematic save logic will be removed entirely.
-   **Action 2: Create a New, Atomic Tool**: Introduce a new function: `create_and_fill_field(pdf_path: str, page_number: int, field_name: str, x0: float, y0: float, x1: float, y1: float, value: str) -> str`.
    -   This tool will handle the entire "create and fill" process in one step.
    -   It will open the PDF, create the widget, set its value, add it to the page, and crucially, **save the output to a new file** (e.g., `original_name_filled.pdf`).
    -   It will return a confirmation message with the path to this new file.
-   **Action 3: Standardize `fill_pdf_form_field`**: Ensure the existing `fill_pdf_form_field` tool also follows the same "save to new file" pattern to maintain consistent behavior. (It already does this, so a review is sufficient).

### **Step 2: Simplify the Agent's Prompt (`prompt.py`)**
-   **File to Modify:** `backend/agents/pdf_filler_manager/prompt.py`
-   **Action:** Rewrite "Workflow B: Create and Fill New Fields".
-   **Change:** Instead of the complex, multi-step process of finding coordinates, creating a field, and then filling it, the agent will now be instructed to do the following for each piece of data:
    1.  Use `find_text_coordinates` to get the location.
    2.  Use the new, single `create_and_fill_field` tool to perform the modification.
-   This makes the agent's logic simpler and less prone to state-related errors.

### **Step 3: Update the Agent's Toolset (`agent.py`)**
-   **File to Modify:** `backend/agents/pdf_filler_manager/agent.py`
-   **Action:** Update the list of tools assigned to the `pdf_filler_manager`.
-   **Change:** Remove `create_text_field` and add the new `create_and_fill_field` tool.
