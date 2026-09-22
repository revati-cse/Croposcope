import os
from werkzeug.utils import secure_filename
from ..utils.file_utils import ensure_dir
from ..ml_model.disease_detector import DiseaseDetector

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MODEL_PATH = os.getenv("MODEL_PATH", "ml-model/models/saved_models/efficientnetv2_crop_disease.h5")

# load model once
detector = DiseaseDetector(MODEL_PATH)


def run_analysis(file, user_id):
    ensure_dir(UPLOAD_FOLDER)

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    prediction, confidence, crop_type = detector.predict(file_path)

    return {
        "crop_type": crop_type,
        "result": prediction,
        "confidence": confidence,
        "image_path": file_path,
    }
