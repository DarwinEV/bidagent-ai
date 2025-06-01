
from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import firestore

get_bids = Blueprint('get_bids', __name__)

@get_bids.route('/api/get_bids', methods=['GET'])
def get_user_bids():
    """Fetch all bids for a user from Firestore."""
    try:
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId parameter'}), 400
        
        # Query Firestore for user's bids
        db = firestore.client()
        bids_ref = db.collection('users').document(user_id).collection('bids')
        bids = bids_ref.order_by('deadline', direction=firestore.Query.DESCENDING).get()
        
        # Convert to list of dictionaries
        result = []
        for bid in bids:
            bid_data = bid.to_dict()
            bid_data['id'] = bid.id  # Add document ID
            result.append(bid_data)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching bids: {str(e)}")
        return jsonify({'error': str(e)}), 500