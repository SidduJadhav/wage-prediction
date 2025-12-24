"""
API Routes for Labour Wage Prediction
"""

from flask import Blueprint, request, jsonify, render_template_string
from models import get_model, get_encoders, get_features, get_metadata
from validators import validate_sector
from predictor import predict_wage
from templates import HTML_TEMPLATE

api = Blueprint('api', __name__)

# ==========================================
# FRONTEND ROUTE
# ==========================================

@api.route('/', methods=['GET'])
def home():
    """Serve HTML frontend for testing"""
    return render_template_string(HTML_TEMPLATE)

# ==========================================
# HEALTH & INFO ROUTES
# ==========================================

@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': {
            'agriculture': get_model('agriculture') is not None,
            'construction': get_model('construction') is not None
        }
    }), 200

@api.route('/api/sectors', methods=['GET'])
def get_sectors():
    """Get list of available sectors"""
    available = [s for s in ['agriculture', 'construction'] if get_model(s) is not None]
    return jsonify({'sectors': available}), 200

@api.route('/api/config', methods=['GET'])
def get_config():
    """Get sector configuration for frontend"""
    config = {}
    
    for sector in ['agriculture', 'construction']:
        if get_model(sector) is None:
            continue
        
        encoders = get_encoders(sector)
        config[sector] = {
            'name': sector.capitalize(),
            'icon': '🌾' if sector == 'agriculture' else '🏗️',
            'metadata': get_metadata(sector),
            'categorical_fields': list(encoders.keys()) if encoders else [],
            'numerical_fields': ['age', 'experience_years', 'skill_level', 'working_hours'],
            'valid_values': {
                col: list(encoders[col].classes_)
                for col in (encoders.keys() if encoders else [])
            }
        }
    
    return jsonify(config), 200

# ==========================================
# PREDICTION ROUTES
# ==========================================

@api.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No data provided'}), 400
        
        sector = payload.get('sector', '').lower().strip()
        data = payload.get('data', {})
        
        if not sector or not data:
            return jsonify({'error': 'Missing sector or data in request'}), 400
        
        # Validate sector
        is_valid, error = validate_sector(sector)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Predict
        success, result = predict_wage(sector, data)
        
        if success:
            return jsonify(result), 200
        else:
            return jsonify({'error': result}), 400
    
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@api.route('/api/test/<sector>', methods=['GET'])
def test_prediction(sector):
    """Test endpoint with pre-configured data"""
    sector = sector.lower().strip()
    
    # Validate sector
    is_valid, error = validate_sector(sector)
    if not is_valid:
        return jsonify({'error': error}), 400
    
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
    
    success, result = predict_wage(sector, test_data[sector])
    
    if success:
        return jsonify(result), 200
    else:
        return jsonify({'error': result}), 400

# ==========================================
# ERROR HANDLERS
# ==========================================

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500