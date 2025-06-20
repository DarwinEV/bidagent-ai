from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from backend.routes import register_routes  # TO DO: fix here to use the correct import - ERR:NO MODULE NAMED BACKEND
from backend.config import load_config

app = Flask(__name__)
CORS(app)

# Load environment variables
config = load_config()

# Register ALL route blueprints
register_routes(app)  # Ensure this is called to register all blueprints

@app.route('/', methods=['GET'])
def index():
    """Returns a simple message for the root URL."""
    return "Welcome to the BidAgents API! Access /api/health for status."


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
    app.run(host='127.0.0.1', port=port, debug=config.get('FLASK_ENV') == 'development')