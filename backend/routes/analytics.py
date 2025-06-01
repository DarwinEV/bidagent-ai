
from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import firestore

analytics = Blueprint('analytics', __name__)

@analytics.route('/api/get_analytics', methods=['GET'])
def get_analytics():
    """Fetch analytics data for a user from Firestore."""
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId parameter'}), 400
        
        # Query Firestore for user's analytics
        db = firestore.client()
        analytics_ref = db.collection('users').document(user_id).collection('analytics').document('summary')
        analytics_doc = analytics_ref.get()
        
        if not analytics_doc.exists:
            # Return default values if no analytics found
            return jsonify({
                'totalBids': 0,
                'bidWinRate': 0,
                'timeSaved': 0,
                'averageBidValue': 0
            })
        
        analytics_data = analytics_doc.to_dict()
        
        return jsonify(analytics_data)
    except Exception as e:
        print(f"Error fetching analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics.route('/api/refresh_analytics', methods=['POST'])
def refresh_analytics():
    """Trigger the Analytics Agent to refresh analytics data."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
        
        # Update Firestore status
        db = firestore.client()
        status_ref = db.collection('users').document(user_id).collection('agentStatus').document('analytics')
        status_ref.set({
            'status': 'running',
            'message': 'Refreshing analytics...',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # In a real app, this would:
        # 1. Trigger the Analytics Agent via Pub/Sub or direct invocation
        # 2. Process historical bid data
        # 3. Update analytics summary in Firestore
        
        # Mock data for now
        analytics_ref = db.collection('users').document(user_id).collection('analytics').document('summary')
        analytics_ref.set({
            'totalBids': 32,
            'bidWinRate': 41,
            'timeSaved': 48,
            'averageBidValue': 125000,
            'lastUpdated': firestore.SERVER_TIMESTAMP
        })
        
        # Update status
        status_ref.update({
            'status': 'completed',
            'message': 'Analytics refreshed successfully',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'success': True,
            'message': 'Analytics refreshed'
        })
    except Exception as e:
        print(f"Error refreshing analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500