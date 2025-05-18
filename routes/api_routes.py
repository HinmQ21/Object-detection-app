import os
import uuid
from flask import Blueprint, request, jsonify

import config
from utils.image_utils import allowed_file, process_image
from tasks.task_manager import create_task, get_task

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and create a detection task
    
    Returns:
        flask.Response: JSON response with task information
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file nào được tải lên'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Không có file nào được chọn'}), 400

    model_name = request.form.get('model', config.DEFAULT_MODEL)

    if model_name not in config.AVAILABLE_MODELS:
        model_name = config.DEFAULT_MODEL

    if file and allowed_file(file.filename):
        task_id = str(uuid.uuid4())
        filename = f"{task_id}.jpg"
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)

        try:
            pil_img = process_image(file)
            pil_img.save(filepath, 'JPEG', quality=95)
            
            create_task(task_id, filepath, model_name)
            
            return jsonify({
                'task_id': task_id,
                'status': config.TASK_STATUS_PENDING,
                'original_image': filepath
            })

        except Exception as e:
            return jsonify({'error': f'Lỗi xử lý hình ảnh: {str(e)}'}), 500

    return jsonify({'error': 'File không hợp lệ'}), 400

@api_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of a task
    
    Args:
        task_id (str): Unique ID for the task
        
    Returns:
        flask.Response: JSON response with task status
    """
    task_data = get_task(task_id)
    
    if task_data is None:
        return jsonify({'error': 'Task not found'}), 404
    
    status = task_data.get('status')
    
    if status == config.TASK_STATUS_PENDING or status == config.TASK_STATUS_PROCESSING:
        return jsonify({
            'task_id': task_id,
            'status': status,
            'original_image': task_data.get('original_image')
        })
    elif status == config.TASK_STATUS_COMPLETED:
        return jsonify({
            'task_id': task_id,
            'status': status,
            'original_image': task_data.get('original_image'),
            'processed_image': task_data.get('processed_image'),
            'detections': task_data.get('detections'),
            'model_used': task_data.get('model_used')
        })
    else:
        return jsonify({
            'task_id': task_id,
            'status': status,
            'error': task_data.get('error', 'Unknown error')
        }), 500
