"""
Load and manage ML models
"""

import joblib
import os
from config import (
    AGRICULTURE_MODEL_DIR, CONSTRUCTION_MODEL_DIR,
    AGRICULTURE_FILES, CONSTRUCTION_FILES
)

# Global model storage
models = {}
encoders = {}
features = {}
metadata = {}

def load_sector_model(sector_name, model_dir, file_config):
    """Load models for a specific sector"""
    try:
        model_path = os.path.join(model_dir, file_config['model'])
        encoder_path = os.path.join(model_dir, file_config['encoders'])
        features_path = os.path.join(model_dir, file_config['features'])
        metadata_path = os.path.join(model_dir, file_config['metadata'])
        
        # Check if directory exists
        if not os.path.isdir(model_dir):
            return False
        
        # Check if critical files exist
        if not all(os.path.exists(p) for p in [model_path, encoder_path, features_path]):
            return False
        
        # Load files
        models[sector_name] = joblib.load(model_path)
        encoders[sector_name] = joblib.load(encoder_path)
        features[sector_name] = joblib.load(features_path)
        
        # Load metadata if exists
        if os.path.exists(metadata_path):
            metadata[sector_name] = joblib.load(metadata_path)
        else:
            metadata[sector_name] = {}
        
        return True
    
    except Exception as e:
        return False

def initialize_models():
    """Initialize all models"""
    load_sector_model('agriculture', AGRICULTURE_MODEL_DIR, AGRICULTURE_FILES)
    load_sector_model('construction', CONSTRUCTION_MODEL_DIR, CONSTRUCTION_FILES)
    
    available_sectors = [k for k, v in models.items() if v is not None]
    return available_sectors

def get_model(sector):
    """Get model for a sector"""
    return models.get(sector)

def get_encoders(sector):
    """Get encoders for a sector"""
    return encoders.get(sector)

def get_features(sector):
    """Get feature names for a sector"""
    return features.get(sector)

def get_metadata(sector):
    """Get metadata for a sector"""
    return metadata.get(sector, {})