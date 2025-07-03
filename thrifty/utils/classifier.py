from ultralytics import YOLO
from pathlib import Path
from django.conf import settings

# Load the model once when this module is imported
model_path = Path(settings.BASE_DIR) / "yolo_training" / "best_classifier.pt"
model = YOLO(str(model_path))

def predict_image_class(image_path):
    """
    Predicts the class of a clothing image using the YOLOv8 classifier.
    
    Args:
        image_path (str or Path): Absolute path to the image file.
    
    Returns:
        str: Predicted class name (e.g., 'dress', 'pants', or 't-shirt').
    """
    results = model.predict(image_path)
    top1_class = results[0].names[results[0].probs.top1]
    return top1_class
