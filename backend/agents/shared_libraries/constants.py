import os
import dotenv

dotenv.load_dotenv()

AGENT_NAME = "main_agent"
DESCRIPTION = "A helpful assistant for bid discovery."
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "EMPTY")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
MODEL = os.getenv("MODEL", "gemini-2.0-flash-001")

# DATASET_ID = os.getenv("DATASET_ID", "products_data_agent")
# TABLE_ID = os.getenv("TABLE_ID", "shoe_items")

DISABLE_WEB_DRIVER = int(os.getenv("DISABLE_WEB_DRIVER", "0"))
WHL_FILE_NAME = os.getenv("ADK_WHL_FILE", "")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "")