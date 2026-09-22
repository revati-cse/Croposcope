# backend/app/routes/upload.py
import os
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
from ..ml_model.disease_detector import DiseaseDetector
from ..utils.file_utils import ensure_dir
from typing import Tuple

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

detector = DiseaseDetector()  # singleton detector instance

@upload_bp.before_app_first_request
def configure():
    # optionally set from env
    current_app.config.setdefault("UPLOAD_DIR", os.environ.get("UPLOAD_DIR", "/app/backend/uploads"))
    ensure_dir(current_app.config["UPLOAD_DIR"])
    current_app.config.setdefault("MAX_CONTENT_LENGTH", MAX_CONTENT_LENGTH)

@upload_bp.route("/", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"ok": False, "error": {"message": "No file part 'image' in request"}}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"ok": False, "error": {"message": "No selected file"}}), 400
    if not allowed_file(file.filename):
        return jsonify({"ok": False, "error": {"message": "Unsupported file type"}}), 400

    filename = secure_filename(file.filename)
    # ensure unique
    save_name = f"{int(__import__('time').time()*1000)}_{filename}"
    save_path = os.path.join(current_app.config["UPLOAD_DIR"], save_name)
    file_bytes = file.read()
    # Basic size check
    if len(file_bytes) > current_app.config["MAX_CONTENT_LENGTH"]:
        return jsonify({"ok": False, "error": {"message": "File too large"}}), 413

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Run inference
    try:
        result = detector.predict_from_bytes(file_bytes, top_k=3)
    except Exception as e:
        current_app.logger.exception("Inference failed")
        return jsonify({"ok": False, "error": {"message": "Inference failed", "detail": str(e)}}), 500

    # Build response (include URL to uploaded file if desired)
    file_url = url_for("static", filename=f"uploads/{save_name}", _external=True) if False else None
    response = {"ok": True, "data": {"file": save_name, "file_url": file_url, "analysis": result}}
    return jsonify(response), 200
