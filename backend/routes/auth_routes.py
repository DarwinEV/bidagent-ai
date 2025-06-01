
from flask import Blueprint, request, jsonify
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/webhook', methods=['POST'])
def clerk_webhook():
    """Handle Clerk webhook events."""
    try:
        event = request.json
        event_type = event.get('type')
        
        # Handle user creation
        if event_type == 'user.created':
            user_data = event.get('data', {})
            user_id = user_data.get('id')
            
            # Store user in Firestore
            # db.collection('users').document(user_id).set({
            #     'email': user_data.get('email_addresses', [{}])[0].get('email_address'),
            #     'firstName': user_data.get('first_name'),
            #     'lastName': user_data.get('last_name'),
            #     'createdAt': firestore.SERVER_TIMESTAMP
            # })
            
            print(f"User created: {user_id}")
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in Clerk webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500