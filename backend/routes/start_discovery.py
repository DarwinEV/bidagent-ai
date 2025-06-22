# THIS ROUTE SHOULD FETCH THE LIST OF SEARCHED BIDS FROM THE search_results sub agent

from flask import Blueprint, request, jsonify
from google.cloud import pubsub_v1
import os
import json
from agents.Bid_Discovery.sub_agents.search_results.agent import bid_search_agent  # Absolute import

start_disc = Blueprint('start_discovery', __name__)

@start_disc.route('/api/start_discovery', methods=['POST'])
async def start_discovery():
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
        bids_string = await bid_search_agent.search_bids(user_id, keywords, naics_codes, geography, portals)

        bids_data = []
        if bids_string:
            try:
                # The agent is prompted to return JSON, so we parse it here.
                bids_data = json.loads(bids_string)
            except json.JSONDecodeError:
                # If the agent fails to return valid JSON, log it and proceed with an empty list.
                print(f"Warning: Could not decode JSON from agent response: {bids_string}")
                bids_data = []

        return jsonify({
            'success': True,
            'message': 'Discovery started',
            'bids': bids_data  # Return the parsed list of bids
        })
    except Exception as e:
        print(f"Error starting discovery: {str(e)}")
        return jsonify({'error': str(e)}), 500