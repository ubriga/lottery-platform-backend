#!/usr/bin/env python3
"""Main Flask application for Israeli Lottery Platform"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

# Initialize Flask app
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
jwt = JWTManager(app)

# Setup logging
logging.basicConfig(
    level=app.config['LOG_LEVEL'],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(app.config['LOG_FILE']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import routes
from api.routes import api_bp
from api.admin import admin_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'name': 'Israeli Lottery Platform API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'games': '/api/games',
            'draws': '/api/draws/<game_id>',
            'stats': '/api/stats/<game_id>',
            'recommendations': '/api/recommendations/<game_id>',
            'admin': '/api/admin/*'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
