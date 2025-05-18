# Object Detection Web Application

A Flask-based web application for object detection using YOLO models. This application allows users to upload images and detect objects using various YOLO models with different performance characteristics.

## Features

- Upload images in various formats (JPEG, PNG, GIF, BMP, WebP)
- Automatic image processing and resizing
- Multiple YOLO model options with different performance/accuracy tradeoffs
- Asynchronous processing with real-time status updates
- Display of original and processed images with bounding boxes
- Detailed detection results including object class and confidence

## Project Structure

```
object_detection_app/
├── app.py                  # Main application entry point
├── config.py               # Application configuration
├── models/                 # Model management
│   └── model_manager.py    # YOLO model loading and management
├── routes/                 # Application routes
│   ├── api_routes.py       # API endpoints
│   └── main_routes.py      # Main web routes
├── static/                 # Static files (CSS, JS, images)
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── uploads/            # Uploaded and processed images
├── tasks/                  # Asynchronous task handling
│   └── task_manager.py     # Task creation and management
├── template/               # HTML templates
│   └── index.html          # Main application page
└── utils/                  # Utility functions
    ├── detection_utils.py  # Object detection utilities
    └── image_utils.py      # Image processing utilities
```

## Requirements

- Python 3.8+
- Flask
- Ultralytics YOLO
- OpenCV
- Pillow (PIL)
- NumPy

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd object_detection_app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. YOLO Models:

   The application uses the following YOLO models:
   - yolo11n.pt (Nano)
   - yolo11s.pt (Small)
   - yolo11m.pt (Medium)
   - yolo11l.pt (Large)
   - yolo11x.pt (XLarge)

   Note: You don't need to download these models manually. The application will automatically download the selected model when it's first used.

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

1. Select a model from the dropdown menu (default is Medium)
2. Click "Choose File" to select an image from your computer
3. Click "Upload" to start the detection process
4. Wait for the processing to complete
5. View the original and processed images with detection results

## Model Options

- **Nano (yolo11n)**: Lightest model, fastest speed, lowest accuracy
- **Small (yolo11s)**: Light model, fast speed, medium accuracy
- **Medium (yolo11m)**: Balanced between speed and accuracy
- **Large (yolo11l)**: Slower, higher accuracy
- **XLarge (yolo11x)**: Slowest, highest accuracy

## Architecture

The application follows a modular architecture:

1. **Flask Web Framework**: Handles HTTP requests and serves web pages
2. **Blueprints**: Separates routes into logical groups (main and API)
3. **Asynchronous Processing**: Uses ThreadPoolExecutor for non-blocking image processing
4. **Task Management**: Tracks the status of detection tasks and provides updates
5. **Model Management**: Loads and caches YOLO models for efficient inference
6. **Image Processing**: Handles various image formats and sizes

## License

[MIT License](LICENSE)
