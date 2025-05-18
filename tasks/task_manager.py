import os
import time
import threading
import concurrent.futures
import cv2
import numpy as np
from PIL import Image

import config
from models.model_manager import get_model
from utils.detection_utils import detect_objects
from utils.image_utils import add_bounding_boxes

task_pool = concurrent.futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL_MAX_WORKERS)
tasks = {}
task_lock = threading.Lock()

def process_detection_task(task_id, filepath, model_name):
    """
    Process the detection task asynchronously
    
    Args:
        task_id (str): Unique ID for the task
        filepath (str): Path to the image file
        model_name (str): Name of the model to use
    """
    try:
        with task_lock:
            if task_id not in tasks:
                return
            tasks[task_id]['status'] = config.TASK_STATUS_PROCESSING

        pil_img = Image.open(filepath)
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        selected_model = get_model(model_name)
        results = detect_objects(cv_img, selected_model)
        
        processed_filename = 'processed_' + os.path.basename(filepath)
        processed_filepath = os.path.join(config.UPLOAD_FOLDER, processed_filename)
        add_bounding_boxes(cv_img, results, processed_filepath)
        
        with task_lock:
            if task_id in tasks:
                tasks[task_id].update({
                    'status': config.TASK_STATUS_COMPLETED,
                    'original_image': filepath,
                    'processed_image': processed_filepath,
                    'detections': results,
                    'model_used': model_name
                })
    except Exception as e:
        print(f"Error processing task {task_id}: {str(e)}")
        with task_lock:
            if task_id in tasks:
                tasks[task_id].update({
                    'status': config.TASK_STATUS_FAILED,
                    'error': str(e)
                })

def create_task(task_id, filepath, model_name):
    """
    Create a new detection task
    
    Args:
        task_id (str): Unique ID for the task
        filepath (str): Path to the image file
        model_name (str): Name of the model to use
    """
    with task_lock:
        tasks[task_id] = {
            'status': config.TASK_STATUS_PENDING,
            'created_at': time.time(),
            'original_image': filepath,
            'model_used': model_name
        }
    
    task_pool.submit(process_detection_task, task_id, filepath, model_name)

def get_task(task_id):
    """
    Get the status and data for a task
    
    Args:
        task_id (str): Unique ID for the task
        
    Returns:
        dict: Task data or None if not found
    """
    with task_lock:
        if task_id not in tasks:
            return None
        return tasks[task_id].copy()

def cleanup_old_tasks():
    """
    Remove tasks older than the configured maximum age
    """
    current_time = time.time()
    with task_lock:
        task_ids_to_remove = []
        for task_id, task_data in tasks.items():
            if current_time - task_data.get('created_at', current_time) > config.TASK_MAX_AGE_SECONDS:
                task_ids_to_remove.append(task_id)
        
        for task_id in task_ids_to_remove:
            del tasks[task_id]

def start_cleanup_timer():
    """
    Start a timer to periodically clean up old tasks
    """
    cleanup_timer = threading.Timer(config.TASK_CLEANUP_INTERVAL_SECONDS, cleanup_old_tasks)
    cleanup_timer.daemon = True
    cleanup_timer.start()
