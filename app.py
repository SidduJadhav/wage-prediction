"""
Labour Wage Prediction API - Main Application
"""

from flask import Flask
from flask_cors import CORS
from config import DEBUG, PORT
from models import initialize_models
from routes import api

# Create Flask app
def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api)
    return app

app = create_app()

# Initialize models on startup
initialize_models()

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == '__main__':
    app.run(
        debug=DEBUG,
        host='0.0.0.0',
        port=PORT,
        threaded=True
    )