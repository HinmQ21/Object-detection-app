from flask import Blueprint, render_template, jsonify

import config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/models', methods=['GET'])
def get_models():
    models_info = {}
    for model_name, model_data in config.AVAILABLE_MODELS.items():
        models_info[model_name] = {
            'description': model_data['description']
        }
    return jsonify({
        'models': models_info,
        'default_model': config.DEFAULT_MODEL
    })
