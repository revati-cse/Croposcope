import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import os
import json
from typing import Tuple, Dict, List
import logging

class CropDiseaseDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or 'ml_model/models/efficientnetv2_crop_disease.h5'
        self.model = None
        self.class_names = []
        self.input_size = (224, 224)
        self.confidence_threshold = 0.7
        
        # Load class names and model
        self._load_class_names()
        self._load_model()
    
    def _load_class_names(self):
        """Load disease class names from JSON file"""
        class_names_path = 'ml_model/models/class_names.json'
        try:
            with open(class_names_path, 'r') as f:
                self.class_names = json.load(f)
        except FileNotFoundError:
            # Default class names from PlantVillage dataset
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
    
    def _load_model(self):
        """Load the trained EfficientNetV2 model"""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                logging.info(f"Model loaded successfully from {self.model_path}")
            else:
                logging.warning(f"Model file not found at {self.model_path}. Using mock predictions.")
                self.model = None
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for model prediction"""
        try:
            # Load and resize image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            image = cv2.resize(image, self.input_size)
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            logging.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def predict_disease(self, image_path: str) -> Dict:
        """Predict crop disease from image"""
        try:
            start_time = tf.timestamp()
            
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            if self.model is None:
                # Mock prediction for demo purposes
                prediction = self._mock_prediction()
            else:
                # Real model prediction
                predictions = self.model.predict(processed_image)
                prediction = self._process_prediction(predictions[0])
            
            end_time = tf.timestamp()
            processing_time = float(end_time - start_time)
            
            prediction['processing_time'] = processing_time
            prediction['model_version'] = 'efficientnetv2-1.0'
            
            return prediction
            
        except Exception as e:
            logging.error(f"Error in disease prediction: {str(e)}")
            return {
                'error': str(e),
                'crop': 'Unknown',
                'disease': 'Analysis Failed',
                'confidence': 0.0,
                'severity': 'unknown'
            }
    
    def _process_prediction(self, predictions: np.ndarray) -> Dict:
        """Process model predictions into readable format"""
        # Get top prediction
        top_prediction_idx = np.argmax(predictions)
        confidence = float(predictions[top_prediction_idx])
        
        if top_prediction_idx < len(self.class_names):
            class_name = self.class_names[top_prediction_idx]
            
            # Parse class name (format: Crop___Disease)
            if '___' in class_name:
                crop, disease = class_name.split('___', 1)
                crop = crop.replace('_', ' ').title()
                disease = disease.replace('_', ' ').title()
            else:
                crop = 'Unknown'
                disease = class_name.replace('_', ' ').title()
            
            # Determine severity based on disease type and confidence
            severity = self._determine_severity(disease, confidence)
            
            return {
                'crop': crop,
                'disease': disease,
                'confidence': confidence,
                'severity': severity,
                'all_predictions': self._get_top_predictions(predictions, 5)
            }
        else:
            return {
                'crop': 'Unknown',
                'disease': 'Unknown Disease',
                'confidence': confidence,
                'severity': 'medium'
            }
    
    def _mock_prediction(self) -> Dict:
        """Generate mock prediction for demo purposes"""
        import random
        
        mock_diseases = [
            ('Tomato', 'Late Blight', 0.94, 'high'),
            ('Potato', 'Early Blight', 0.87, 'medium'),
            ('Corn', 'Northern Leaf Blight', 0.91, 'medium'),
            ('Tomato', 'Bacterial Spot', 0.89, 'low'),
            ('Apple', 'Apple Scab', 0.85, 'medium'),
            ('Grape', 'Black Rot', 0.92, 'high')
        ]
        
        crop, disease, confidence, severity = random.choice(mock_diseases)
        
        return {
            'crop': crop,
            'disease': disease,
            'confidence': confidence,
            'severity': severity,
            'all_predictions': []
        }
    
    def _determine_severity(self, disease: str, confidence: float) -> str:
        """Determine disease severity based on disease type and confidence"""
        high_severity_diseases = [
            'late blight', 'black rot', 'fire blight', 'bacterial wilt'
        ]
        
        low_severity_diseases = [
            'leaf spot', 'powdery mildew', 'rust'
        ]
        
        disease_lower = disease.lower()
        
        if any(severe_disease in disease_lower for severe_disease in high_severity_diseases):
            return 'high'
        elif any(mild_disease in disease_lower for mild_disease in low_severity_diseases):
            return 'low'
        else:
            # Medium severity by default, adjust by confidence
            if confidence > 0.9:
                return 'medium'
            elif confidence > 0.8:
                return 'low'
            else:
                return 'medium'
    
    def _get_top_predictions(self, predictions: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Get top K predictions with class names and confidences"""
        top_indices = np.argsort(predictions)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self.class_names):
                class_name = self.class_names[idx]
                confidence = float(predictions[idx])
                
                if '___' in class_name:
                    crop, disease = class_name.split('___', 1)
                    crop = crop.replace('_', ' ').title()
                    disease = disease.replace('_', ' ').title()
                else:
                    crop = 'Unknown'
                    disease = class_name.replace('_', ' ').title()
                
                results.append({
                    'crop': crop,
                    'disease': disease,
                    'confidence': confidence
                })
        
        return results