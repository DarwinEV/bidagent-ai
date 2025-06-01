
from flask import Blueprint, request, jsonify
from pubsub_publish import publish_message
import os
import firebase_admin
from firebase_admin import firestore

submit_bid = Blueprint('submit_bid', __name__)

@submit_bid.route('/api/submit_via_email', methods=['POST'])
def submit_via_email():
    """Trigger the Notification Agent to submit a bid via email."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        bid_id = payload.get('bidId')
        
        if not all([user_id, bid_id]):
            return jsonify({'error': 'Missing required fields: userId, bidId'}), 400
        
        # Get bid details from Firestore
        db = firestore.client()
        bid_ref = db.collection('users').document(user_id).collection('bids').document(bid_id)
        bid_doc = bid_ref.get()
        
        if not bid_doc.exists:
            return jsonify({'error': f'Bid {bid_id} not found'}), 404
        
        bid_data = bid_doc.to_dict()
        
        # Update Firestore status
        status_ref = db.collection('users').document(user_id).collection('agentStatus').document('submitting')
        status_ref.set({
            'status': 'running',
            'message': 'Submitting bid via email...',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Publish to Pub/Sub for email submission
        topic_name = os.environ.get('PUBSUB_TOPIC_NOTIFY', 'bid-notify')
        message_id = publish_message(topic_name, {
            'userId': user_id,
            'bidId': bid_id,
            'title': bid_data.get('title', 'Unknown Bid'),
            'deadline': bid_data.get('deadline'),
            'prefilledPath': bid_data.get('prefilledPath')
        })
        
        # Update bid status in Firestore
        bid_ref.update({
            'status': 'submitted',
            'submittedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'success': True,
            'message': 'Bid submission via email started',
            'messageId': message_id
        })
    except Exception as e:
        print(f"Error submitting bid via email: {str(e)}")
        return jsonify({'error': str(e)}), 500