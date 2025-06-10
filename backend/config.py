
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    # Load from .env file if it exists
    load_dotenv()
    
    # Required environment variables
    required_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET'
    ]
    
    # Check for missing required variables
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    # if missing_vars:
    #     raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Return dictionary of config values
    return {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
        'FIREBASE_PROJECT_ID': os.environ.get('FIREBASE_PROJECT_ID'),
        'FIREBASE_STORAGE_BUCKET': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'SENDGRID_API_KEY': os.environ.get('SENDGRID_API_KEY'),
        'PUBSUB_TOPIC_DISCOVERY': os.environ.get('PUBSUB_TOPIC_DISCOVERY', 'bid-discovery'),
        'PUBSUB_TOPIC_DOWNLOAD': os.environ.get('PUBSUB_TOPIC_DOWNLOAD', 'bid-download'),
        'PUBSUB_TOPIC_ANALYSIS': os.environ.get('PUBSUB_TOPIC_ANALYSIS', 'bid-analysis'),
        'PUBSUB_TOPIC_PREFILL': os.environ.get('PUBSUB_TOPIC_PREFILL', 'bid-prefill'),
        'PUBSUB_TOPIC_NOTIFY': os.environ.get('PUBSUB_TOPIC_NOTIFY', 'bid-notify')
    }
