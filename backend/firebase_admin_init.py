import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

def initialize_firebase_app(config):
    """
    Initializes the Firebase Admin SDK.
    In a Google Cloud environment (like Cloud Run), the SDK automatically
    detects the project's service account and credentials.
    In a local environment, it uses the GOOGLE_APPLICATION_CREDENTIALS
    environment variable.
    """
    if not firebase_admin._apps:
        project_id = getattr(config, 'FIREBASE_PROJECT_ID', None)
        storage_bucket = getattr(config, 'FIREBASE_STORAGE_BUCKET', None)

        if not project_id:
            raise ValueError("FIREBASE_PROJECT_ID not configured.")

        # On Cloud Run, credentials are automatically discovered.
        # Locally, the SDK uses GOOGLE_APPLICATION_CREDENTIALS env var.
        firebase_admin.initialize_app(options={
            'projectId': project_id,
            'storageBucket': storage_bucket
        })
        print(f"Firebase Admin SDK initialized for project {project_id}")

    db = firestore.client()
    bucket = storage.bucket()
    return db, bucket

# This is a placeholder for any other initialization logic you might need.
# For now, it just calls the main initialization function.
def initialize_firebase():
    """Legacy wrapper for initialization."""
    # This function is kept for compatibility if it's called elsewhere,
    # but it doesn't receive the config object, so direct calls might fail
    # if the environment is not perfectly set up.
    # The primary initialization should happen via initialize_firebase_app in app.py
    if not firebase_admin._apps:
        # Attempt to initialize with environment variables directly for legacy calls
        print("Legacy Firebase initialization attempt...")
        project_id = os.environ.get('FIREBASE_PROJECT_ID')
        storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET')
        if project_id:
            firebase_admin.initialize_app(options={
                'projectId': project_id,
                'storageBucket': storage_bucket
            })
    
    return firestore.client(), storage.bucket()