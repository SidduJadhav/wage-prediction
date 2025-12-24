"""
Configuration settings for Labour Wage Prediction API
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
TIMEOUT = int(os.getenv('API_TIMEOUT', 10))

# Model Directories
AGRICULTURE_MODEL_DIR = 'Agriculture_prediction_models'
CONSTRUCTION_MODEL_DIR = 'Construction_prediction_models'

# Model file names
AGRICULTURE_FILES = {
    'model': 'xgboost_wage_model.pkl',
    'encoders': 'label_encoders.pkl',
    'features': 'feature_names.pkl',
    'metadata': 'model_metadata.pkl'
}

CONSTRUCTION_FILES = {
    'model': 'construction_wage_model.pkl',
    'encoders': 'construction_label_encoders.pkl',
    'features': 'construction_feature_names.pkl',
    'metadata': 'construction_model_metadata.pkl'
}