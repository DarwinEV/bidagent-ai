# THIS ROUTE SHOULD FETCH THE LIST OF SEARCHED BIDS FROM THE search_results sub agent

from flask import Blueprint, request, jsonify
import os
import json
from backend.agents.Bid_Discovery.sub_agents.search_results.agent import bid_search_agent  # Absolute import

start_disc = Blueprint('start_discovery', __name__)

@start_disc.route('/api/start_discovery', methods=['POST'])
def start_discovery():
    """Start the bid discovery process by triggering the Orchestrator Agent."""
    try:
        payload = request.json
        user_id = payload.get('userId')
        keywords = payload.get('keywords', '')
        naics_codes = payload.get('naicsCodes', '')
        geography = payload.get('geography', '')
        portals = payload.get('portals', [])

        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400

        # Fetch bids using the search_results sub-agent
        bids = bid_search_agent.search_bids(keywords, naics_codes, geography, portals)

        return jsonify({
            'success': True,
            'message': 'Discovery started',
            'bids': bids  # Return the list of bids
        })
    except Exception as e:
        print(f"Error starting discovery: {str(e)}")
        return jsonify({'error': str(e)}), 500