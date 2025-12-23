"""
Labour Wage Prediction API - Production Ready
Runs on Render, Azure, Heroku, or local machine
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# FLASK APP INITIALIZATION
# ==========================================
app = Flask(__name__)
CORS(app)

# Configuration
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
TIMEOUT = int(os.getenv('API_TIMEOUT', 10))

# ==========================================
# LOAD MODELS AND ENCODERS
# ==========================================
print("="*70)
print("LOADING MODELS")
print("="*70)

models = {}
encoders = {}
features = {}
metadata = {}

def load_sector_model(sector_name, model_dir):
    """Load models for a specific sector"""
    try:
        print(f"\n[Loading] {sector_name.capitalize()}...")
        
        model_path = os.path.join(model_dir, f'{sector_name}_wage_model.pkl')
        encoder_path = os.path.join(model_dir, f'{sector_name}_label_encoders.pkl')
        features_path = os.path.join(model_dir, f'{sector_name}_feature_names.pkl')
        metadata_path = os.path.join(model_dir, f'{sector_name}_model_metadata.pkl')
        
        # Check if files exist
        if not all(os.path.exists(p) for p in [model_path, encoder_path, features_path, metadata_path]):
            missing = []
            if not os.path.exists(model_path):
                missing.append(f"Model: {model_path}")
            if not os.path.exists(encoder_path):
                missing.append(f"Encoders: {encoder_path}")
            if not os.path.exists(features_path):
                missing.append(f"Features: {features_path}")
            if not os.path.exists(metadata_path):
                missing.append(f"Metadata: {metadata_path}")
            
            print(f"❌ {sector_name.capitalize()} - Missing files:")
            for missing_file in missing:
                print(f"   {missing_file}")
            return False
        
        # Load files
        models[sector_name] = joblib.load(model_path)
        encoders[sector_name] = joblib.load(encoder_path)
        features[sector_name] = joblib.load(features_path)
        metadata[sector_name] = joblib.load(metadata_path)
        
        print(f"✓ {sector_name.capitalize()} model loaded successfully!")
        print(f"  Features: {features[sector_name]}")
        print(f"  Categorical fields: {list(encoders[sector_name].keys())}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to load {sector_name} model: {e}")
        return False

# Load both models
load_sector_model('agriculture', 'Agriculture_prediction_models')
load_sector_model('construction', 'Construction_prediction_models')

print("\n" + "="*70)
available_sectors = [k for k, v in models.items() if v is not None]
print(f"✓ Available sectors: {available_sectors}")
print("="*70 + "\n")

# ==========================================
# VALIDATION HELPER
# ==========================================
def validate_input(sector, data):
    """
    Validate input data against training data.
    Returns: (is_valid, error_message_or_data)
    """
    if sector not in models or models[sector] is None:
        return False, f"Sector '{sector}' model not loaded. Available: {list(models.keys())}"
    
    # Check for required fields
    required_fields = features[sector]
    provided_fields = set(data.keys())
    
    missing = set(required_fields) - provided_fields
    if missing:
        return False, f"Missing required fields: {list(missing)}"
    
    # Validate categorical values
    categorical_cols = list(encoders[sector].keys())
    for col in categorical_cols:
        if col in data:
            value = data[col]
            if isinstance(value, str):
                value = value.strip()
            
            valid_values = list(encoders[sector][col].classes_)
            if value not in valid_values:
                return False, f"Invalid value '{value}' for field '{col}'. Valid options: {valid_values}"
    
    return True, data

# ==========================================
# ROUTES
# ==========================================

@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API info"""
    return jsonify({
        'app': 'Labour Wage Prediction API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'config': '/api/config',
            'predict': '/api/predict (POST)',
            'sectors': '/api/sectors',
            'test': '/api/test/{sector}'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'agriculture': models.get('agriculture') is not None,
            'construction': models.get('construction') is not None
        }
    }), 200

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get sector configuration for frontend"""
    config = {
        'agriculture': {
            'name': 'Agriculture',
            'icon': '🌾',
            'metadata': metadata.get('agriculture', {}),
            'categorical_fields': list(encoders['agriculture'].keys()) if 'agriculture' in encoders else [],
            'numerical_fields': ['age', 'experience_years', 'skill_level', 'working_hours'],
            'valid_values': {
                col: list(encoders['agriculture'][col].classes_)
                for col in encoders.get('agriculture', {}).keys()
            }
        },
        'construction': {
            'name': 'Construction',
            'icon': '🏗️',
            'metadata': metadata.get('construction', {}),
            'categorical_fields': list(encoders['construction'].keys()) if 'construction' in encoders else [],
            'numerical_fields': ['age', 'experience_years', 'skill_level', 'working_hours'],
            'valid_values': {
                col: list(encoders['construction'][col].classes_)
                for col in encoders.get('construction', {}).keys()
            }
        }
    }
    return jsonify(config), 200

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get list of available sectors"""
    available = [k for k, v in models.items() if v is not None]
    return jsonify({'sectors': available}), 200

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Request body:
    {
        "sector": "agriculture" or "construction",
        "data": {
            "age": 35,
            "experience_years": 15,
            ...
        }
    }
    """
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No data provided'}), 400
        
        sector = payload.get('sector', '').lower().strip()
        data = payload.get('data', {})
        
        if not sector or not data:
            return jsonify({'error': 'Missing sector or data in request'}), 400
        
        print("\n" + "="*60)
        print(f"PREDICTION REQUEST - {sector.upper()}")
        print("="*60)
        print(f"Input data: {data}")
        
        # Validate input
        is_valid, result = validate_input(sector, data)
        if not is_valid:
            print(f"❌ Validation failed: {result}")
            return jsonify({'error': result}), 400
        
        # Prepare DataFrame
        df = pd.DataFrame([data])
        print(f"\nOriginal DataFrame:\n{df}")
        
        # Get categorical columns
        categorical_cols = list(encoders[sector].keys())
        
        # Encode categorical variables
        print("\nEncoding categorical variables:")
        for col in categorical_cols:
            if col in df.columns:
                original_value = df[col].values[0]
                
                # Strip whitespace but preserve case
                if isinstance(original_value, str):
                    original_value = original_value.strip()
                
                try:
                    encoded = encoders[sector][col].transform([original_value])[0]
                    df[col] = int(encoded)
                    print(f"  ✓ {col}: '{original_value}' → {encoded}")
                except ValueError as e:
                    error_msg = f"Encoding error for {col}: {str(e)}"
                    print(f"  ❌ {error_msg}")
                    return jsonify({'error': error_msg}), 400
        
        print(f"\nEncoded DataFrame:\n{df}")
        
        # Ensure correct feature order
        df = df[features[sector]]
        print(f"\nFinal feature order:\n{df}")
        
        # Make prediction
        prediction = float(models[sector].predict(df)[0])
        
        # Ensure non-negative prediction
        if prediction < 0:
            prediction = 0
            print("⚠️  Prediction was negative, set to 0")
        
        print(f"\n✅ PREDICTION: ₹{prediction:.2f}")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'predicted_wage': round(prediction, 2),
            'sector': sector,
            'monthly_estimate': round(prediction * 26, 2),
            'annual_estimate': round(prediction * 312, 2),
            'input_data': data
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@app.route('/api/test/<sector>', methods=['GET'])
def test_prediction(sector):
    """Test endpoint with pre-configured data"""
    sector = sector.lower().strip()
    
    if sector not in models or models[sector] is None:
        return jsonify({'error': f'Model for {sector} not loaded'}), 500
    
    test_data = {
        'agriculture': {
            'age': 35,
            'experience_years': 15,
            'education_level': 'secondary',
            'occupation': 'tractor operator',
            'skill_level': 3,
            'state': 'MH',
            'working_hours': 9,
            'employment_type': 'permanent'
        },
        'construction': {
            'age': 32,
            'experience_years': 10,
            'education_level': 'diploma',
            'job_role': 'electrician',
            'skill_level': 3,
            'city_tier': 'Metro',
            'working_hours': 8,
            'employment_type': 'contract',
            'project_type': 'commercial'
        }
    }
    
    if sector not in test_data:
        return jsonify({'error': f'No test data for {sector}'}), 400
    
    # Use predict logic
    try:
        data = test_data[sector]
        is_valid, _ = validate_input(sector, data)
        
        if not is_valid:
            return jsonify({'error': 'Test data invalid'}), 400
        
        df = pd.DataFrame([data])
        categorical_cols = list(encoders[sector].keys())
        
        for col in categorical_cols:
            if col in df.columns:
                original_value = df[col].values[0]
                if isinstance(original_value, str):
                    original_value = original_value.strip()
                encoded = encoders[sector][col].transform([original_value])[0]
                df[col] = int(encoded)
        
        df = df[features[sector]]
        prediction = float(models[sector].predict(df)[0])
        
        if prediction < 0:
            prediction = 0
        
        return jsonify({
            'success': True,
            'predicted_wage': round(prediction, 2),
            'sector': sector,
            'monthly_estimate': round(prediction * 26, 2),
            'input_data': data,
            'message': f'{sector.capitalize()} model test successful!'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==========================================
# RUN APPLICATION
# ==========================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 LABOUR WAGE PREDICTION - FLASK BACKEND")
    print("="*70)
    print(f"\n📍 Environment: {'Development' if DEBUG else 'Production'}")
    print(f"📍 Port: {PORT}")
    print(f"📍 Debug: {DEBUG}")
    print("\n📍 API Endpoints:")
    print(f"  • Home: http://localhost:{PORT}/")
    print(f"  • Health: http://localhost:{PORT}/health")
    print(f"  • Config: http://localhost:{PORT}/api/config")
    print(f"  • Sectors: http://localhost:{PORT}/api/sectors")
    print(f"  • Predict: POST http://localhost:{PORT}/api/predict")
    print(f"  • Test: http://localhost:{PORT}/api/test/agriculture")
    print("\n⚠️  Console shows detailed prediction logs")
    print("="*70 + "\n")
    
    # Use 0.0.0.0 for production (needed for Render)
    app.run(
        debug=DEBUG,
        host='0.0.0.0',
        port=PORT,
        threaded=True
    )