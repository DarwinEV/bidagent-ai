# search_results/agent.py

# this is the sub agent that search for bids
# TO DO: NEED TO PASS IN THE BID SEARCH PARAMETERS LIKE KEYWORDS/SERVICES, NAICS CODES, GEPGRAPHIC FOCUS (DROPDOWN) AND PORTAL SELECTION
# TO DO: NEED TO OBTAIN THE LIST OF BIDS BACK TO THE FRONTEND

import time
import warnings
import asyncio
import uuid
import io

import selenium
from google.adk.agents.llm_agent import Agent
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from PIL import Image
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from ....shared_libraries import constants
from . import prompt

warnings.filterwarnings("ignore", category=UserWarning)

class BidSearchAgent(Agent):
    async def search_bids(self, user_id, keywords, naics_codes, geography, portals):
        """
        Uses the LLM agent to search for bids based on the provided criteria.
        """
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        app_name = "bid_discovery"
        session_id = str(uuid.uuid4())
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        runner = Runner(
            agent=self,
            app_name=app_name,
            session_service=session_service,
            artifact_service=artifact_service,
        )

        initial_prompt = (
            "Start a search on the following portals:"
            f" {', '.join(portals) if portals else 'any relevant portal'}."
            f" Use the following criteria: Keywords='{keywords}',"
            f" NAICS Codes='{naics_codes}', Geography='{geography}'."
            " Find the top 3 bid opportunities and return their details in a JSON format."
        )
        
        user_content = types.Content(role='user', parts=[types.Part(text=initial_prompt)])
        final_response = None
        
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text

        return final_response

driver = None


def get_driver():
    """Initializes and returns a singleton Chrome WebDriver instance."""
    global driver
    if driver is None and not constants.DISABLE_WEB_DRIVER:
        print("🚀 Initializing new Chrome WebDriver instance...")
        options = Options()
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--verbose")
        # Use a unique user data directory to prevent session conflicts
        user_data_dir = f"/tmp/selenium_{uuid.uuid4()}"
        options.add_argument(f"user-data-dir={user_data_dir}")
        driver = selenium.webdriver.Chrome(options=options)
    return driver


def go_to_url(url: str) -> str:
    """Navigates the browser to the given URL."""
    print(f"🌐 Navigating to URL: {url}")  # Added print statement
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    local_driver.get(url.strip())
    return f"Navigated to URL: {url}"


async def take_screenshot(tool_context: ToolContext) -> dict:
    """Takes a screenshot and saves it with the given filename. called 'load artifacts' after to load the image"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    print(f"📸 Taking screenshot and saving as: {filename}")
    local_driver = get_driver()
    if not local_driver:
        return {"status": "error", "message": "WebDriver is disabled."}
    local_driver.save_screenshot(filename)

    # Save page source for debugging
    page_source_filename = f"page_source_{timestamp}.html"
    with open(page_source_filename, "w", encoding="utf-8") as f:
        f.write(local_driver.page_source)
    print(f"📄 Page source saved as: {page_source_filename}")

    image = Image.open(filename)

    # Correctly encode the image to PNG bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
    )

    return {"status": "ok", "filename": filename}


def _find_element(driver, selector: dict) -> WebElement | None:
    """Tries to find an element using a chain of robust selectors."""
    strategies = [
        (By.ID, selector.get("id")),
        (By.NAME, selector.get("name")),
        (By.CSS_SELECTOR, selector.get("css")),
        (By.XPATH, selector.get("xpath")),
    ]
    for by, value in strategies:
        if value:
            try:
                return driver.find_element(by, value)
            except NoSuchElementException:
                continue
    return None


def click_at_coordinates(x: int, y: int) -> str:
    """Clicks at the specified coordinates on the screen."""
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    local_driver.execute_script(f"window.scrollTo({x}, {y});")
    local_driver.find_element(By.TAG_NAME, "body").click()
    return "Clicked at coordinates."


def find_element_with_text(text: str) -> str:
    """Finds an element on the page with the given text."""
    print(f"🔍 Finding element with text: '{text}'")  # Added print statement
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    try:
        element = local_driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
        if element:
            return "Element found."
        else:
            return "Element not found."
    except NoSuchElementException:
        return "Element not found."
    except ElementNotInteractableException:
        return "Element not interactable, cannot click."


def click_element_with_text(text: str) -> str:
    """Clicks on an element on the page with the given text."""
    print(f"🖱️ Clicking element with text: '{text}'")  # Added print statement
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    try:
        element = local_driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
        element.click()
        return f"Clicked element with text: {text}"
    except NoSuchElementException:
        return "Element not found, cannot click."
    except ElementNotInteractableException:
        return "Element not interactable, cannot click."
    except ElementClickInterceptedException:
        return "Element click intercepted, cannot click."


def enter_text_into_element(text_to_enter: str, selector: dict, press_enter_after: bool = False) -> str:
    """Enters text into an element found by the given selector, optionally pressing Enter."""
    print(
        f"📝 Entering text '{text_to_enter}' into element found by: {selector}"
    )
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."

    element = _find_element(local_driver, selector)
    if element:
        try:
            text_to_send = text_to_enter
            if press_enter_after:
                text_to_send += Keys.RETURN
            element.send_keys(text_to_send)
            
            message = f"Entered text '{text_to_enter}' into element found by {selector}"
            if press_enter_after:
                message += " and pressed Enter."
            return message
        except ElementNotInteractableException:
            return "Element not interactable, cannot enter text."
    else:
        return f"Element not found with selector: {selector}"


def enter_text_into_element_by_label(label_text: str, text_to_enter: str) -> str:
    """Finds an input field by its label text and enters text into it."""
    print(f"📝 Entering text '{text_to_enter}' into field labeled '{label_text}'")
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    try:
        # Find the label element
        label_element = local_driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]")
        
        # Get the 'for' attribute to find the associated input
        input_id = label_element.get_attribute('for')
        if input_id:
            input_element = local_driver.find_element(By.ID, input_id)
            input_element.send_keys(text_to_enter)
            return f"Entered text '{text_to_enter}' into field with ID '{input_id}' (labeled '{label_text}')."
        else:
            return f"Label '{label_text}' found, but it has no 'for' attribute."

    except NoSuchElementException:
        return f"Could not find a label containing the text '{label_text}' or its associated input field."
    except ElementNotInteractableException:
        return f"Input field for label '{label_text}' is not interactable."


def scroll_down_screen() -> str:
    """Scrolls down the screen by a moderate amount."""
    print("⬇️ scroll the screen")  # Added print statement
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    local_driver.execute_script("window.scrollBy(0, 500)")
    return "Scrolled down the screen."


def get_page_source() -> str:
    LIMIT = 1000000
    """Returns the current page source."""
    print("📄 Getting page source...")  # Added print statement
    local_driver = get_driver()
    if not local_driver:
        return "WebDriver is disabled."
    return local_driver.page_source[0:LIMIT]


def analyze_webpage_and_determine_action(
    page_source: str, user_task: str, tool_context: ToolContext
) -> str:
    """Analyzes the webpage and determines the next action (scroll, click, etc.)."""
    print(
        "🤔 Analyzing webpage and determining next action..."
    )  # Added print statement

    analysis_prompt = f"""
    You are an expert web page analyzer.
    You have been tasked with controlling a web browser to achieve a user's goal.
    The user's task is: {user_task}
    Here is the current HTML source code of the webpage:
    ```html
    {page_source}
    ```

    Based on the webpage content and the user's task, determine the next best action to take.
    Consider actions like: completing page source, scrolling down to see more content, clicking on links or buttons to navigate, or entering text into input fields.

    Think step-by-step:
    1. Briefly analyze the user's task and the webpage content.
    2. If source code appears to be incomplete, complete it to make it valid html. Keep the product titles as is. Only complete missing html syntax
    3. Identify potential interactive elements on the page (links, buttons, input fields, etc.).
    4. Determine if scrolling is necessary to reveal more content.
    5. Decide on the most logical next action to progress towards completing the user's task.

    Your response should be a concise action plan, choosing from these options:
    - "COMPLETE_PAGE_SOURCE": If source code appears to be incomplete, complte it to make it valid html
    - "SCROLL_DOWN": If more content needs to be loaded by scrolling.
    - "CLICK: <element_text>": If a specific element with text <element_text> should be clicked. Replace <element_text> with the actual text of the element.
    - "ENTER_TEXT: <selector_json>, <text_to_enter>, <press_enter>": If text needs to be entered into an input field. Replace <selector_json> with a JSON object like {"id": "search_box_id"}, <text_to_enter> with the text, and <press_enter> with true or false.
    - "ENTER_TEXT_BY_LABEL: <label_text>, <text_to_enter>": If text needs to be entered into an input field identified by its label.
    - "TASK_COMPLETED": If you believe the user's task is likely completed on this page.
    - "STUCK": If you are unsure what to do next or cannot progress further.
    - "ASK_USER": If you need clarification from the user on what to do next.

    If you choose "CLICK" or "ENTER_TEXT", ensure the element text or ID is clearly identifiable from the webpage source. If multiple similar elements exist, choose the most relevant one based on the user's task.
    If you are unsure, or if none of the above actions seem appropriate, default to "ASK_USER".

    Example Responses:
    - SCROLL_DOWN
    - CLICK: Learn more
    - ENTER_TEXT: {"id": "search_box_id"}, Gemini API, false
    - ENTER_TEXT: {"name": "keyword-text"}, New Jersey, true
    - ENTER_TEXT_BY_LABEL: Username, my_user_name
    - TASK_COMPLETED
    - STUCK
    - ASK_USER

    What is your action plan?
    """
    return analysis_prompt


bid_search_agent = BidSearchAgent(
    model=constants.MODEL,
    name="bid_search_agent",
    description="Search procurement websites like SAM.gov or state portals to find and return "
        "the top 3 relevant bid opportunities based on user-provided filters such as keywords, NAICS codes, "
        "location, and preferred portals.",
    instruction=prompt.SEARCH_RESULT_AGENT_PROMPT,
    tools=[
        go_to_url,
        take_screenshot,
        click_at_coordinates,
        find_element_with_text,
        click_element_with_text,
        enter_text_into_element,
        enter_text_into_element_by_label,
        scroll_down_screen,
        get_page_source,
        load_artifacts_tool,
        analyze_webpage_and_determine_action,
    ],
)