
import os
import json
import base64
import time
from google.cloud import pubsub_v1, secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
from pubsub_publish import publish_message

# This would use Gemini for embeddings in a real implementation
def compute_relevance(bid_description, user_keywords):
    """Simulate relevance computation using simple keyword matching.
    
    In a real implementation, this would use Vertex AI Embeddings for
    semantic similarity.
    """
    score = 0
    for keyword in user_keywords:
        if keyword.lower() in bid_description.lower():
            score += 1
    
    # Normalize score between 0 and 1
    return min(1.0, score / max(1, len(user_keywords)))

def discovery_agent(event, context):
    """Bid Discovery Agent entry point - triggered by Pub/Sub message.
    
    This agent is responsible for:
    1. Reading credentials from Secret Manager
    2. Crawling procurement portals
    3. Computing relevance scores
    4. Publishing filtered bids to the download topic
    
    Args:
        event (dict): The Pub/Sub event
        context (google.cloud.functions.Context): The event context
    """
    print(f"Bid Discovery Agent triggered: {context.event_id}")
    
    # Decode the message
    if 'data' in event:
        data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    else:
        data = {}
    
    user_id = data.get('userId')
    keywords = data.get('keywords', [])
    portals = data.get('portals', [])
    credentials_id = data.get('credentialsId')
    
    if not user_id:
        print("Error: Missing userId in message")
        return
    
    # Initialize Firestore
    db = firestore.client()
    
    # Update agent status
    status_ref = db.collection('users').document(user_id).collection('agentStatus').document('discovery')
    status_ref.update({
        'message': f'Searching {len(portals)} portals for relevant bids...',
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    try:
        # Mock portal crawling results - in a real app, this would use Playwright
        mock_bids = [
            {
                'bidId': f'bid-{int(time.time())}-1',
                'url': 'https://sam.gov/opportunity/12345',
                'title': 'HVAC System Replacement - Building 42',
                'description': 'Replace existing HVAC system with energy-efficient units for Building 42. Includes removal of old equipment and installation of new 5-ton units.',
                'deadline': '2025-06-15',
                'agency': 'State University',
                'location': 'Sacramento, CA'
            },
            {
                'bidId': f'bid-{int(time.time())}-2',
                'url': 'https://sam.gov/opportunity/67890',
                'title': 'Network Infrastructure Upgrade',
                'description': 'Upgrade network infrastructure including switches, routers, and cabling for city hall building.',
                'deadline': '2025-06-20',
                'agency': 'City of San Francisco',
                'location': 'San Francisco, CA'
            },
            {
                'bidId': f'bid-{int(time.time())}-3',
                'url': 'https://sam.gov/opportunity/54321',
                'title': 'Landscaping Services Contract',
                'description': 'Ongoing landscaping and maintenance services for municipal parks and recreational facilities.',
                'deadline': '2025-07-01',
                'agency': 'Parks Department',
                'location': 'Los Angeles, CA'
            }
        ]
        
        # Filter bids by relevance
        filtered_bids = []
        relevance_threshold = 0.3  # Minimum relevance score to include a bid
        
        for bid in mock_bids:
            relevance = compute_relevance(bid['description'], keywords)
            if relevance >= relevance_threshold:
                bid['relevanceScore'] = relevance
                filtered_bids.append(bid)
                
                # Store bid in Firestore
                bid_ref = db.collection('users').document(user_id).collection('bids').document(bid['bidId'])
                bid_ref.set({
                    'title': bid['title'],
                    'agency': bid['agency'],
                    'deadline': bid['deadline'],
                    'location': bid['location'],
                    'description': bid['description'],
                    'url': bid['url'],
                    'relevanceScore': relevance,
                    'status': 'discovered',
                    'discoveredAt': firestore.SERVER_TIMESTAMP
                })
        
        # Publish filtered bids to download topic
        if filtered_bids:
            topic_name = os.environ.get('PUBSUB_TOPIC_DOWNLOAD', 'bid-download')
            message_id = publish_message(topic_name, {
                'userId': user_id,
                'filteredBids': filtered_bids
            })
            
            print(f"Published {len(filtered_bids)} filtered bids with message ID: {message_id}")
            
            # Update status
            status_ref.update({
                'status': 'completed',
                'message': f'Found {len(filtered_bids)} relevant bids out of {len(mock_bids)} total bids.',
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        else:
            # No relevant bids found
            status_ref.update({
                'status': 'completed',
                'message': f'No relevant bids found matching your criteria.',
                'timestamp': firestore.SERVER_TIMESTAMP
            })
    
    except Exception as e:
        print(f"Error in Discovery Agent: {str(e)}")
        status_ref.update({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'timestamp': firestore.SERVER_TIMESTAMP
        })

if __name__ == "__main__":
    # For local testing
    test_event = {
        'data': base64.b64encode(json.dumps({
            'userId': 'test-user-123',
            'keywords': ['HVAC', 'plumbing'],
            'portals': ['sam.gov', 'state.ca.gov/bids'],
            'credentialsId': 'secret://users/test-user-123/portalCreds',
            'subscriptionTier': 'Basic'
        }).encode('utf-8'))
    }
    
    class Context:
        def __init__(self, event_id):
            self.event_id = event_id
    
    discovery_agent(test_event, Context('test-event-123'))