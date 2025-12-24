"""
Wage prediction logic
"""

import pandas as pd
from models import get_model, get_encoders, get_features
from validators import validate_input

def predict_wage(sector, data):
    """
    Predict wage for given sector and worker data
    Returns: (success, result_or_error)
    """
    try:
        # Validate input
        is_valid, result = validate_input(sector, data)
        if not is_valid:
            return False, result
        
        # Prepare DataFrame
        df = pd.DataFrame([data])
        
        # Get encoders and encode categorical variables
        encoders = get_encoders(sector)
        categorical_cols = list(encoders.keys())
        
        for col in categorical_cols:
            if col in df.columns:
                original_value = df[col].values[0]
                if isinstance(original_value, str):
                    original_value = original_value.strip()
                
                try:
                    encoded = encoders[col].transform([original_value])[0]
                    df[col] = int(encoded)
                except ValueError as e:
                    return False, f"Encoding error for {col}: {str(e)}"
        
        # Ensure correct feature order
        feature_names = get_features(sector)
        df = df[feature_names]
        
        # Make prediction
        model = get_model(sector)
        prediction = float(model.predict(df)[0])
        
        # Ensure non-negative prediction
        if prediction < 0:
            prediction = 0
        
        # Calculate estimates
        result = {
            'success': True,
            'predicted_wage': round(prediction, 2),
            'sector': sector,
            'monthly_estimate': round(prediction * 26, 2),
            'annual_estimate': round(prediction * 312, 2),
            'input_data': data
        }
        
        return True, result
    
    except Exception as e:
        return False, str(e)