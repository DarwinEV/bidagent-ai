
from flask import Blueprint, request, jsonify
from pubsub_publish import publish_message
import os
import firebase_admin
from firebase_admin import firestore
import json

start_disc = Blueprint('start_discovery', __name__)

@start_disc.route('/api/start_discovery', methods=['POST'])
def start_discovery():
    """Start the bid discovery process by triggering the Orchestrator Agent."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
        
        # Write a Firestore doc for job status
        db = firestore.client()
        status_ref = db.collection('users').document(user_id).collection('agentStatus').document('discovery')
        status_ref.set({
            'status': 'running',
            'message': 'Starting bid discovery...',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Publish to Pub/Sub
        topic_name = os.environ.get('PUBSUB_TOPIC_DISCOVERY', 'bid-discovery')
        message_id = publish_message(topic_name, payload)
        
        return jsonify({
            'success': True,
            'message': 'Discovery started',
            'messageId': message_id
        })
    except Exception as e:
        print(f"Error starting discovery: {str(e)}")
        return jsonify({'error': str(e)}), 500