from flask import Blueprint
from .auth_routes import auth_bp
from .start_discovery import start_disc
from .download_bid import download_bid
from .fill_bid import fill_bid
from .submit_bid import submit_bid
from .get_bids import get_bids
from .get_agent_status import agent_status
from .analytics import analytics

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
