
from google.cloud import pubsub_v1
import os
import json

def publish_message(topic_name, data):
    """Publish a message to a Pub/Sub topic.
    
    Args:
        topic_name (str): The Pub/Sub topic name
        data (dict): The message payload as a dictionary
    
    Returns:
        str: The message ID
    """
    project_id = os.environ.get('FIREBASE_PROJECT_ID')
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    
    # Convert dict to JSON string then to bytes
    data_bytes = json.dumps(data).encode('utf-8')
    
    # Publish message
    future = publisher.publish(topic_path, data_bytes)
    message_id = future.result()
    
    print(f"Published message to {topic_path} with ID: {message_id}")
    return message_id