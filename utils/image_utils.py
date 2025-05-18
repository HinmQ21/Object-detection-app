"""
Image processing utilities
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageOps
import config

def allowed_file(filename):
    """
    Check if the file has an allowed extension
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if the file has an allowed extension, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def process_image(file_stream):
    """
    Process uploaded image:
    1. Convert to supported format if needed
    2. Resize if too large
    3. Return PIL Image object
    
    Args:
        file_stream: File-like object containing the image
        
    Returns:
        PIL.Image: Processed image
    """
    img = Image.open(file_stream)

    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    h, w = img.size
    if max(h, w) > config.MODEL_SZ:
        scale = config.MODEL_SZ / max(h, w)
        new_width = int(w * scale)
        new_height = int(h * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    img = ImageOps.fit(img, (config.MODEL_SZ, config.MODEL_SZ), method=Image.LANCZOS, centering=(0.5, 0.5))

    return img

def add_bounding_boxes(image, detections, output_path):
    """
    Add bounding boxes to an image and save it
    
    Args:
        image (numpy.ndarray): OpenCV image
        detections (list): List of detection results
        output_path (str): Path to save the output image
    """
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        label = f"{det['class']} {det['confidence']:.2f}"

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 1

        (label_width, label_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        cv2.rectangle(image, (x1, y1 - label_height - 10), (x1 + label_width, y1), (0, 255, 0), -1)

        cv2.putText(image, label, (x1, y1 - 5), font, font_scale, (0, 0, 0), thickness)

    cv2.imwrite(output_path, image)
