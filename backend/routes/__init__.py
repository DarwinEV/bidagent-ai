
from flask import Blueprint
from routes.auth_routes import auth_bp
from routes.start_discovery import start_disc
from routes.download_bid import download_bid
from routes.fill_bid import fill_bid
from routes.submit_bid import submit_bid
from routes.get_bids import get_bids
from routes.get_agent_status import agent_status
from routes.analytics import analytics

def register_routes(app):
    """Register all route blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(start_disc)
    app.register_blueprint(download_bid)
    app.register_blueprint(fill_bid)
    app.register_blueprint(submit_bid)
    app.register_blueprint(get_bids)
    app.register_blueprint(agent_status)
    app.register_blueprint(analytics)
    
    return app
