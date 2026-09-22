# backend/app/ml_model/model_loader.py
import os
from typing import Tuple, Dict
import threading
import json

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/ml-model/models/saved_models/efficientnetv2_crop_disease.h5")
CLASS_MAP_PATH = os.environ.get("CLASS_MAP_PATH", "/app/ml-model/models/saved_models/class_names.json")

_lock = threading.Lock()
_model = None
_class_map = None

def load_tf_model() -> Tuple[tf.keras.Model, Dict[int, str]]:
    global _model, _class_map
    if _model is not None and _class_map is not None:
        return _model, _class_map

    with _lock:
        if _model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
            _model = load_model(MODEL_PATH, compile=False)
        if _class_map is None:
            if os.path.exists(CLASS_MAP_PATH):
                with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
                    names = json.load(f)
                    # Accept either list or dict
                    if isinstance(names, list):
                        _class_map = {i: n for i, n in enumerate(names)}
                    else:
                        _class_map = {int(k): v for k, v in names.items()}
            else:
                _class_map = {}
    return _model, _class_map

def preprocess_image_bytes(img_bytes: bytes, target_size=(384, 384)) -> np.ndarray:
    """Decode bytes, resize, normalize. Returns batch of shape (1, H, W, C)"""
    img = image.load_img(
        path=tf.io.BytesIO(img_bytes),
        target_size=target_size
    )
    arr = image.img_to_array(img)
    arr = tf.keras.applications.efficientnet.preprocess_input(arr)  # uses same preprocessing family
    arr = np.expand_dims(arr, axis=0)
    return arr
