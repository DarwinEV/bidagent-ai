
import firebase_admin
from firebase_admin import credentials, firestore, storage, secretmanager
import os
import json

def initialize_firebase():
    """Initialize Firebase Admin SDK with application credentials."""
    # Check if already initialized
    if firebase_admin._apps:
        # Get existing app
        app = firebase_admin._apps['[DEFAULT]']
        db = firestore.client()
        bucket = storage.bucket()
        sm_client = secretmanager.SecretManagerServiceClient()
        return db, bucket, sm_client
    
    # Path to service account credentials
    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.environ.get('FIREBASE_PROJECT_ID')
    bucket_name = os.environ.get('FIREBASE_STORAGE_BUCKET')
    
    if not cred_path or not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
    
    # Initialize Firebase Admin
    cred = credentials.Certificate(cred_path)
    app = firebase_admin.initialize_app(cred, {
        'projectId': project_id,
        'storageBucket': bucket_name
    })
    
    # Get services
    db = firestore.client()
    bucket = storage.bucket()
    sm_client = secretmanager.SecretManagerServiceClient()
    
    print(f"Firebase Admin SDK initialized for project {project_id}")
    return db, bucket, sm_client