from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from firebase_admin_init import initialize_firebase
from routes import register_routes
from config import load_config

app = Flask(__name__)
CORS(app)

# Load environment variables
config = load_config()

# Initialize Firebase Admin SDK
db, storage, secret_manager = initialize_firebase()

# Register route blueprints
register_routes(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/api/onboard', methods=['POST'])
def onboard():
    """Process user onboarding data and store in Firestore."""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
        
        # Store user profile in Firestore
        db.collection('users').document(user_id).set({
            'email': data.get('email'),
            'role': data.get('role'),
            'onboardingCompleted': True,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        
        # If company data URL is provided, process it
        company_data_url = data.get('companyDataUrl')
        if company_data_url:
            # Process and store company data
            pass
            
        return jsonify({'success': True, 'message': 'Onboarding complete'})
    except Exception as e:
        print(f"Error in onboarding: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.get('FLASK_ENV') == 'development')