import sys
print("--- Starting app.py execution ---")
sys.stdout.flush()

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from routes import register_routes
from config import load_config

# Configure logging to be verbose and output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

logging.info("--- Python script starting, modules imported ---")

try:
    logging.info("Initializing Flask app object...")
    app = Flask(__name__)
    logging.info("Flask app object initialized.")
    CORS(app)
    logging.info("CORS configured.")

    # Load environment variables
    logging.info("Loading configuration...")
    config = load_config()
    logging.info("Configuration loaded successfully.")

    # Register ALL route blueprints
    logging.info("Registering route blueprints...")
    register_routes(app)
    logging.info("Route blueprints registered successfully.")
    
    logging.info("--- Application setup complete, routes registered ---")

except Exception as e:
    logging.critical(f"CRITICAL ERROR during application setup: {e}", exc_info=True)
    print(f"CRITICAL ERROR during application setup: {e}")
    sys.stdout.flush()
    raise

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
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting development server on http://0.0.0.0:{port}...")
    app.run(host='0.0.0.0', port=port)