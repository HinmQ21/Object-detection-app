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

    w, h = img.size
    if max(h, w) > config.MODEL_SZ:
        scale = config.MODEL_SZ / max(h, w)
        new_width = int(w * scale)
        new_height = int(h * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    # img = ImageOps.fit(img, (config.MODEL_SZ, config.MODEL_SZ), method=Image.LANCZOS, centering=(0.5, 0.5))

    return img

def add_bounding_boxes(image, detections, output_path):
    """
    Add bounding boxes to an image and save it

    Args:
        image (numpy.ndarray): OpenCV image
        detections (list): List of detection results
        output_path (str): Path to save the output image
    """
    img_h, img_w = image.shape[:2]

    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        label = f"{det['class']} {det['confidence']:.2f}"

        # Lấy kích thước nhãn
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 1
        (label_width, label_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        margin = 5  # khoảng cách giữa box và text

        # Tính vị trí vẽ text: ưu tiên vẽ phía trên, nếu không đủ chỗ thì vẽ phía dưới
        # y_text_top là toạ độ Y cho cạnh trên của background rectangle
        if y1 - label_height - margin - baseline >= 0:
            y_text_top = y1 - label_height - margin
            y_text_bottom = y1
        else:
            # Nếu không đủ khoảng trống phía trên, vẽ ở dưới box
            y_text_top = y2 + margin
            y_text_bottom = y2 + label_height + margin + baseline
            # đảm bảo không vượt quá ảnh
            if y_text_bottom > img_h:
                y_text_bottom = img_h
                y_text_top = img_h - label_height - baseline

        # Tính vị trí X cho text: đảm bảo không vượt biên trái/phải
        x_text_left = max(x1, 0)
        if x1 + label_width > img_w:
            x_text_left = img_w - label_width

        # Vẽ bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Vẽ background cho label
        cv2.rectangle(
            image,
            (x_text_left, y_text_top),
            (x_text_left + label_width, y_text_bottom),
            (0, 255, 0),
            cv2.FILLED
        )

        # Vẽ text label
        cv2.putText(
            image,
            label,
            (x_text_left, y_text_bottom - baseline),
            font,
            font_scale,
            (0, 0, 0),
            thickness
        )

    # Lưu ảnh kết quả
    cv2.imwrite(output_path, image)