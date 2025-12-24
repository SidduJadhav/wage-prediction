"""
Input validation for predictions
"""

from models import get_encoders, get_features, get_model

def validate_input(sector, data):
    """
    Validate input data against training data.
    Returns: (is_valid, error_message_or_data)
    """
    # Check if model exists
    if get_model(sector) is None:
        available = [k for k in ['agriculture', 'construction'] if get_model(k) is not None]
        return False, f"Sector '{sector}' model not loaded. Available: {available}"
    
    # Check for required fields
    required_fields = get_features(sector)
    provided_fields = set(data.keys())
    
    missing = set(required_fields) - provided_fields
    if missing:
        return False, f"Missing required fields: {list(missing)}"
    
    # Validate categorical values
    encoders = get_encoders(sector)
    categorical_cols = list(encoders.keys())
    
    for col in categorical_cols:
        if col in data:
            value = data[col]
            if isinstance(value, str):
                value = value.strip()
            
            valid_values = list(encoders[col].classes_)
            if value not in valid_values:
                return False, f"Invalid value '{value}' for field '{col}'. Valid options: {valid_values}"
    
    return True, data

def validate_sector(sector):
    """Check if sector model is loaded"""
    if get_model(sector) is None:
        available = [k for k in ['agriculture', 'construction'] if get_model(k) is not None]
        return False, f"Sector '{sector}' not available. Available: {available}"
    return True, None