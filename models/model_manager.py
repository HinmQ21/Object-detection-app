from ultralytics import YOLO
import config

loaded_models = {}

def get_model(model_name):
    if model_name not in config.AVAILABLE_MODELS:
        model_name = config.DEFAULT_MODEL

    if model_name not in loaded_models:
        model_path = config.AVAILABLE_MODELS[model_name]['path']
        try:
            loaded_models[model_name] = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            if config.DEFAULT_MODEL not in loaded_models:
                loaded_models[config.DEFAULT_MODEL] = YOLO(config.AVAILABLE_MODELS[config.DEFAULT_MODEL]['path'])
            return loaded_models[config.DEFAULT_MODEL]

    return loaded_models[model_name]

default_model = get_model(config.DEFAULT_MODEL)
