
from flask import Blueprint, request, jsonify
from pubsub_publish import publish_message
import os

download_bid = Blueprint('download_bid', __name__)

@download_bid.route('/api/download_bid', methods=['POST'])
def download_bid_handler():
    """Manually trigger the Document Access Agent to download a bid document."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        bid_id = payload.get('bidId')
        url = payload.get('url')
        
        if not all([user_id, bid_id, url]):
            return jsonify({'error': 'Missing required fields: userId, bidId, url'}), 400
        
        # Publish to Pub/Sub for document download
        topic_name = os.environ.get('PUBSUB_TOPIC_DOWNLOAD', 'bid-download')
        message_id = publish_message(topic_name, {
            'userId': user_id,
            'filteredBids': [{
                'bidId': bid_id,
                'url': url,
                'title': payload.get('title', 'Unknown Bid')
            }]
        })
        
        return jsonify({
            'success': True,
            'message': 'Document download started',
            'messageId': message_id
        })
    except Exception as e:
        print(f"Error triggering document download: {str(e)}")
        return jsonify({'error': str(e)}), 500