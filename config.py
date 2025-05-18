import os

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_IMAGE_DIMENSION = 1280
MODEL_SZ = 640

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model settings
AVAILABLE_MODELS = {
    'yolo11n': {
        'path': 'yolo11n.pt',
        'description': 'Nano - Nhẹ nhất, tốc độ nhanh nhất, độ chính xác thấp nhất'
    },
    'yolo11s': {
        'path': 'yolo11s.pt',
        'description': 'Small - Nhẹ, tốc độ nhanh, độ chính xác trung bình'
    },
    'yolo11m': {
        'path': 'yolo11m.pt',
        'description': 'Medium - Cân bằng giữa tốc độ và độ chính xác'
    },
    'yolo11l': {
        'path': 'yolo11l.pt',
        'description': 'Large - Chậm hơn, độ chính xác cao'
    },
    'yolo11x': {
        'path': 'yolo11x.pt',
        'description': 'XLarge - Chậm nhất, độ chính xác cao nhất'
    }
}

DEFAULT_MODEL = 'yolo11m'

# Task settings
TASK_STATUS_PENDING = 'pending'
TASK_STATUS_PROCESSING = 'processing'
TASK_STATUS_COMPLETED = 'completed'
TASK_STATUS_FAILED = 'failed'

# Thread pool settings
THREAD_POOL_MAX_WORKERS = 4

# Task cleanup settings
TASK_MAX_AGE_SECONDS = 3600  # 1 hour
TASK_CLEANUP_INTERVAL_SECONDS = 900  # 15 minutes
