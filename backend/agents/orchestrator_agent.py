
# import os
# import json
# import base64
# from google.cloud import pubsub_v1
# import firebase_admin
# from firebase_admin import credentials, firestore
# from pubsub_publish import publish_message

# def orchestrator_agent(event, context):
#     """Orchestrator Agent entry point - triggered by Pub/Sub message.
    
#     This agent is responsible for:
#     1. Reading user profile & subscription tier from Firestore
#     2. Creating a DiscoverTask message and publishing to Pub/Sub
#     3. Monitoring job status in Firestore
    
#     Args:
#         event (dict): The Pub/Sub event
#         context (google.cloud.functions.Context): The event context
#     """
#     print(f"Orchestrator Agent triggered: {context.event_id}")
    
#     # Decode the message
#     if 'data' in event:
#         data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
#     else:
#         data = {}
    
#     user_id = data.get('userId')
#     keywords = data.get('keywords', [])
#     portals = data.get('portals', [])
    
#     if not user_id:
#         print("Error: Missing userId in message")
#         return
    
#     # Initialize Firestore
#     db = firestore.client()
    
#     # Update agent status
#     status_ref = db.collection('users').document(user_id).collection('agentStatus').document('discovery')
#     status_ref.update({
#         'message': 'Orchestrator agent processing request...',
#         'timestamp': firestore.SERVER_TIMESTAMP
#     })
    
#     try:
#         # Fetch user profile to get subscription tier
#         user_ref = db.collection('users').document(user_id)
#         user_doc = user_ref.get()
        
#         if not user_doc.exists:
#             print(f"Error: User {user_id} not found")
#             status_ref.update({
#                 'status': 'error',
#                 'message': 'User not found',
#                 'timestamp': firestore.SERVER_TIMESTAMP
#             })
#             return
        
#         user_data = user_doc.to_dict()
#         subscription_tier = user_data.get('subscriptionTier', 'Basic')
        
#         # Create DiscoverTask message
#         discover_task = {
#             'userId': user_id,
#             'keywords': keywords,
#             'portals': portals,
#             'credentialsId': f"secret://users/{user_id}/portalCreds",
#             'subscriptionTier': subscription_tier
#         }
        
#         # Publish to Bid Discovery topic
#         topic_name = os.environ.get('PUBSUB_TOPIC_DISCOVERY', 'bid-discovery')
#         message_id = publish_message(topic_name, discover_task)
        
#         print(f"Published DiscoverTask message with ID: {message_id}")
        
#         # Update status
#         status_ref.update({
#             'message': f'Discovery request forwarded to discovery agent. Searching {len(portals)} portals for "{", ".join(keywords)}".',
#             'timestamp': firestore.SERVER_TIMESTAMP
#         })
        
#     except Exception as e:
#         print(f"Error in Orchestrator Agent: {str(e)}")
#         status_ref.update({
#             'status': 'error',
#             'message': f'Error: {str(e)}',
#             'timestamp': firestore.SERVER_TIMESTAMP
#         })

# if __name__ == "__main__":
#     # For local testing
#     test_event = {
#         'data': base64.b64encode(json.dumps({
#             'userId': 'test-user-123',
#             'keywords': ['HVAC', 'plumbing'],
#             'portals': ['sam.gov', 'state.ca.gov/bids']
#         }).encode('utf-8'))
#     }
    
#     class Context:
#         def __init__(self, event_id):
#             self.event_id = event_id
    
#     orchestrator_agent(test_event, Context('test-event-123'))