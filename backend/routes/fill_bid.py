
from flask import Blueprint, request, jsonify
from pubsub_publish import publish_message
import os
import firebase_admin
from firebase_admin import firestore

fill_bid = Blueprint('fill_bid', __name__)

@fill_bid.route('/api/fill_bid', methods=['POST'])
def fill_bid_handler():
    """Trigger the Proposal Pre-Fill Agent to fill a bid document with company data."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        bid_id = payload.get('bidId')
        fields = payload.get('fields', {})
        
        if not all([user_id, bid_id]):
            return jsonify({'error': 'Missing required fields: userId, bidId'}), 400
        
        # Update Firestore status
        db = firestore.client()
        status_ref = db.collection('users').document(user_id).collection('agentStatus').document('filling')
        status_ref.set({
            'status': 'running',
            'message': 'Pre-filling bid document...',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Publish to Pub/Sub for document pre-fill
        topic_name = os.environ.get('PUBSUB_TOPIC_PREFILL', 'bid-prefill')
        message_id = publish_message(topic_name, {
            'userId': user_id,
            'bidId': bid_id,
            'extractedFields': fields
        })
        
        return jsonify({
            'success': True,
            'message': 'Document pre-fill started',
            'messageId': message_id
        })
    except Exception as e:
        print(f"Error triggering document pre-fill: {str(e)}")
        return jsonify({'error': str(e)}), 500
