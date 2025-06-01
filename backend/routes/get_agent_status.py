
from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import firestore

agent_status = Blueprint('agent_status', __name__)

@agent_status.route('/api/agent_status', methods=['GET'])
def get_agent_status():
    """Fetch the status of all agents for a user from Firestore."""
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId parameter'}), 400
        
        # Query Firestore for agent statuses
        db = firestore.client()
        status_ref = db.collection('users').document(user_id).collection('agentStatus')
        statuses = status_ref.get()
        
        # Default status for all agents
        result = {
            'discovery': {'status': 'idle', 'message': '', 'lastUpdated': ''},
            'filling': {'status': 'idle', 'message': '', 'lastUpdated': ''},
            'submitting': {'status': 'idle', 'message': '', 'lastUpdated': ''},
            'notifications': {'status': 'idle', 'message': '', 'lastUpdated': ''},
            'analytics': {'status': 'idle', 'message': '', 'lastUpdated': ''}
        }
        
        # Update with actual statuses from Firestore
        for status in statuses:
            agent_name = status.id
            status_data = status.to_dict()
            
            if agent_name in result:
                result[agent_name] = {
                    'status': status_data.get('status', 'idle'),
                    'message': status_data.get('message', ''),
                    'lastUpdated': status_data.get('timestamp', '').isoformat() 
                        if hasattr(status_data.get('timestamp', ''), 'isoformat') else ''
                }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching agent status: {str(e)}")
        return jsonify({'error': str(e)}), 500
