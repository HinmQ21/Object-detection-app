"""
Object detection utilities
"""
import config
from models.model_manager import default_model

def detect_objects(image, selected_model=None):
    detection_model = selected_model if selected_model is not None else default_model

    results = detection_model(image, imgsz=config.MODEL_SZ)

    detections = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = detection_model.names[cls]

            detections.append({
                'class': name,
                'confidence': round(conf, 2),
                'bbox': [x1, y1, x2, y2]
            })

    return detections
