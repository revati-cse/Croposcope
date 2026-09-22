import os
import json
import pickle
import tensorflow as tf
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class ModelLoader:
    """Handles loading and management of ML models"""
    
    def __init__(self, model_dir: str = "ml_model/models/saved_models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.model_metadata = {}
        self.class_names = []
        self.model_version = "1.0"
        
    def load_model(self, model_name: str = "efficientnetv2_crop_disease.h5") -> bool:
        """Load TensorFlow model from file"""
        model_path = self.model_dir / model_name
        
        try:
            if not model_path.exists():
                logger.warning(f"Model file not found at {model_path}")
                return False
            
            # Load the model
            self.model = tf.keras.models.load_model(str(model_path))
            logger.info(f"Model loaded successfully from {model_path}")
            
            # Load metadata if available
            self._load_model_metadata()
            
            # Load class names
            self._load_class_names()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False
    
    def _load_model_metadata(self):
        """Load model metadata from JSON file"""
        metadata_path = self.model_dir / "model_metadata.json"
        
        try:
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                self.model_version = self.model_metadata.get('version', '1.0')
                logger.info("Model metadata loaded successfully")
            else:
                # Default metadata
                self.model_metadata = {
                    'version': '1.0',
                    'architecture': 'EfficientNetV2B0',
                    'input_shape': [224, 224, 3],
                    'num_classes': len(self.class_names) if self.class_names else 38,
                    'framework': 'TensorFlow',
                    'preprocessing': {
                        'normalization': 'imagenet',
                        'resize_method': 'bilinear',
                        'data_format': 'channels_last'
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to load model metadata: {str(e)}")
    
    def _load_class_names(self):
        """Load class names from JSON file"""
        class_names_path = self.model_dir / "class_names.json"
        
        try:
            if class_names_path.exists():
                with open(class_names_path, 'r') as f:
                    self.class_names = json.load(f)
                logger.info(f"Loaded {len(self.class_names)} class names")
            else:
                # Default PlantVillage class names
                self.class_names = [
                    'Apple___Apple_scab',
                    'Apple___Black_rot',
                    'Apple___Cedar_apple_rust',
                    'Apple___healthy',
                    'Blueberry___healthy',
                    'Cherry_(including_sour)___Powdery_mildew',
                    'Cherry_(including_sour)___healthy',
                    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                    'Corn_(maize)___Common_rust_',
                    'Corn_(maize)___Northern_Leaf_Blight',
                    'Corn_(maize)___healthy',
                    'Grape___Black_rot',
                    'Grape___Esca_(Black_Measles)',
                    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                    'Grape___healthy',
                    'Orange___Haunglongbing_(Citrus_greening)',
                    'Peach___Bacterial_spot',
                    'Peach___healthy',
                    'Pepper,_bell___Bacterial_spot',
                    'Pepper,_bell___healthy',
                    'Potato___Early_blight',
                    'Potato___Late_blight',
                    'Potato___healthy',
                    'Raspberry___healthy',
                    'Soybean___healthy',
                    'Squash___Powdery_mildew',
                    'Strawberry___Leaf_scorch',
                    'Strawberry___healthy',
                    'Tomato___Bacterial_spot',
                    'Tomato___Early_blight',
                    'Tomato___Late_blight',
                    'Tomato___Leaf_Mold',
                    'Tomato___Septoria_leaf_spot',
                    'Tomato___Spider_mites Two-spotted_spider_mite',
                    'Tomato___Target_Spot',
                    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                    'Tomato___Tomato_mosaic_virus',
                    'Tomato___healthy'
                ]
                logger.info("Using default PlantVillage class names")
                
        except Exception as e:
            logger.error(f"Failed to load class names: {str(e)}")
    
    def predict(self, processed_image: np.ndarray) -> Optional[np.ndarray]:
        """Make prediction using loaded model"""
        if self.model is None:
            logger.error("Model not loaded")
            return None
        
        try:
            # Ensure correct input shape
            if len(processed_image.shape) == 3:
                processed_image = np.expand_dims(processed_image, axis=0)
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if self.model is None:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'version': self.model_version,
            'metadata': self.model_metadata,
            'num_classes': len(self.class_names),
            'class_names_sample': self.class_names[:5] if self.class_names else [],
            'input_shape': self.model.input_shape if self.model else None,
            'output_shape': self.model.output_shape if self.model else None
        }
        
        return info
    
    def validate_model(self) -> bool:
        """Validate model is working correctly"""
        if self.model is None:
            return False
        
        try:
            # Create dummy input
            dummy_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
            
            # Test prediction
            prediction = self.model.predict(dummy_input, verbose=0)
            
            # Check output shape
            expected_classes = len(self.class_names)
            if prediction.shape[1] != expected_classes:
                logger.warning(f"Model output shape mismatch: expected {expected_classes}, got {prediction.shape[1]}")
                return False
            
            # Check prediction is valid probability distribution
            if not np.allclose(np.sum(prediction, axis=1), 1.0, atol=1e-6):
                logger.warning("Model output is not a valid probability distribution")
                return False
            
            logger.info("Model validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            return False
    
    def save_model_metadata(self, metadata: Dict[str, Any]):
        """Save model metadata to file"""
        metadata_path = self.model_dir / "model_metadata.json"
        
        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model metadata saved to {metadata_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model metadata: {str(e)}")
    
    def save_class_names(self, class_names: list):
        """Save class names to file"""
        class_names_path = self.model_dir / "class_names.json"
        
        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            
            with open(class_names_path, 'w') as f:
                json.dump(class_names, f, indent=2)
            
            self.class_names = class_names
            logger.info(f"Class names saved to {class_names_path}")
            
        except Exception as e:
            logger.error(f"Failed to save class names: {str(e)}")
    
    def convert_to_tflite(self, output_path: str = None) -> bool:
        """Convert loaded model to TensorFlow Lite format"""
        if self.model is None:
            logger.error("No model loaded for conversion")
            return False
        
        try:
            if output_path is None:
                output_path = str(self.model_dir / "model.tflite")
            
            # Convert model
            converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            tflite_model = converter.convert()
            
            # Save converted model
            with open(output_path, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"Model converted to TensorFlow Lite: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"TensorFlow Lite conversion failed: {str(e)}")
            return False

# Global model loader instance
model_loader = ModelLoader()