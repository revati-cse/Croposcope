import numpy as np
import json
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class PredictionPostprocessor:
    """Post-processing for ML model predictions"""
    
    def __init__(self, class_names_path: str = None):
        self.class_names = []
        self.confidence_threshold = 0.5
        self.severity_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.0
        }
        
        # Disease severity mapping based on disease types
        self.disease_severity_map = {
            'late_blight': 'high',
            'early_blight': 'medium',
            'bacterial_spot': 'medium',
            'leaf_mold': 'low',
            'powdery_mildew': 'low',
            'healthy': 'low'
        }
        
        # Load class names if path provided
        if class_names_path:
            self.load_class_names(class_names_path)
    
    def load_class_names(self, class_names_path: str):
        """Load class names from JSON file"""
        try:
            with open(class_names_path, 'r') as f:
                self.class_names = json.load(f)
            logger.info(f"Loaded {len(self.class_names)} class names")
        except Exception as e:
            logger.error(f"Failed to load class names: {str(e)}")
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
    
    def parse_class_name(self, class_name: str) -> Tuple[str, str]:
        """Parse crop and disease from class name"""
        if '___' in class_name:
            crop, disease = class_name.split('___', 1)
            
            # Clean crop name
            crop = crop.replace('_', ' ')
            crop = crop.replace('(maize)', '')
            crop = crop.replace('(including_sour)', '')
            crop = crop.replace(',_bell', '')
            crop = crop.strip().title()
            
            # Clean disease name
            disease = disease.replace('_', ' ')
            disease = disease.replace('  ', ' ')
            disease = disease.strip().title()
            
            # Handle special cases
            if 'healthy' in disease.lower():
                disease = 'Healthy'
            
            return crop, disease
        else:
            return 'Unknown', class_name.replace('_', ' ').title()
    
    def determine_severity(self, crop: str, disease: str, confidence: float) -> str:
        """Determine disease severity based on disease type and confidence"""
        disease_lower = disease.lower()
        
        # Check specific disease patterns
        high_severity_patterns = [
            'late blight', 'black rot', 'fire blight', 'bacterial wilt',
            'haunglongbing', 'citrus greening', 'esca', 'black measles'
        ]
        
        medium_severity_patterns = [
            'early blight', 'bacterial spot', 'leaf blight', 'common rust',
            'northern leaf blight', 'cercospora', 'target spot', 'mosaic virus'
        ]
        
        low_severity_patterns = [
            'healthy', 'powdery mildew', 'leaf mold', 'leaf scorch',
            'spider mites', 'septoria'
        ]
        
        # Check patterns
        for pattern in high_severity_patterns:
            if pattern in disease_lower:
                return 'high'
        
        for pattern in medium_severity_patterns:
            if pattern in disease_lower:
                return 'medium'
        
        for pattern in low_severity_patterns:
            if pattern in disease_lower:
                return 'low'
        
        # Fall back to confidence-based severity
        if confidence > self.severity_thresholds['high']:
            return 'high'
        elif confidence > self.severity_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def get_treatment_suggestions(self, crop: str, disease: str, severity: str) -> List[str]:
        """Get basic treatment suggestions based on disease"""
        disease_lower = disease.lower()
        
        treatment_map = {
            'late blight': [
                'Apply copper-based organic fungicide',
                'Improve air circulation between plants',
                'Remove infected plant material immediately',
                'Avoid overhead watering'
            ],
            'early blight': [
                'Apply baking soda spray (1 tbsp per liter)',
                'Use crop rotation with non-solanaceous plants',
                'Mulch around plants to prevent soil splash',
                'Ensure proper plant spacing'
            ],
            'bacterial spot': [
                'Use copper soap spray',
                'Avoid overhead irrigation',
                'Remove affected leaves',
                'Practice crop rotation'
            ],
            'powdery mildew': [
                'Apply neem oil spray',
                'Improve air circulation',
                'Use baking soda solution',
                'Remove affected leaves'
            ],
            'leaf mold': [
                'Reduce humidity around plants',
                'Improve ventilation',
                'Apply organic fungicide',
                'Remove infected foliage'
            ],
            'healthy': [
                'Continue current care practices',
                'Monitor regularly for early detection',
                'Maintain proper nutrition',
                'Ensure adequate spacing'
            ]
        }
        
        # Find matching treatments
        for key, treatments in treatment_map.items():
            if key in disease_lower:
                return treatments
        
        # Default treatments
        if 'healthy' in disease_lower:
            return treatment_map['healthy']
        else:
            return [
                'Consult agricultural extension service',
                'Apply appropriate organic treatment',
                'Monitor plant closely',
                'Maintain good cultural practices'
            ]
    
    def process_predictions(self, predictions: np.ndarray, 
                          top_k: int = 5,
                          return_all: bool = False) -> Dict[str, Any]:
        """Process model predictions into structured result"""
        try:
            # Get prediction probabilities
            if len(predictions.shape) > 1:
                predictions = predictions[0]  # Remove batch dimension
            
            # Get top prediction
            top_idx = np.argmax(predictions)
            top_confidence = float(predictions[top_idx])
            
            if top_idx < len(self.class_names):
                class_name = self.class_names[top_idx]
                crop, disease = self.parse_class_name(class_name)
            else:
                crop, disease = 'Unknown', 'Unknown Disease'
            
            # Determine severity
            severity = self.determine_severity(crop, disease, top_confidence)
            
            # Get treatment suggestions
            treatments = self.get_treatment_suggestions(crop, disease, severity)
            
            # Prepare result
            result = {
                'crop': crop,
                'disease': disease,
                'confidence': top_confidence,
                'severity': severity,
                'treatments': treatments,
                'is_healthy': 'healthy' in disease.lower(),
                'requires_attention': severity in ['medium', 'high']
            }
            
            # Add top K predictions if requested
            if return_all or top_k > 1:
                top_indices = np.argsort(predictions)[-top_k:][::-1]
                all_predictions = []
                
                for idx in top_indices:
                    if idx < len(self.class_names):
                        class_name = self.class_names[idx]
                        pred_crop, pred_disease = self.parse_class_name(class_name)
                        confidence = float(predictions[idx])
                        
                        all_predictions.append({
                            'crop': pred_crop,
                            'disease': pred_disease,
                            'confidence': confidence,
                            'class_index': int(idx)
                        })
                
                result['all_predictions'] = all_predictions
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process predictions: {str(e)}")
            return {
                'crop': 'Unknown',
                'disease': 'Processing Error',
                'confidence': 0.0,
                'severity': 'unknown',
                'treatments': ['Please try again with a clearer image'],
                'error': str(e)
            }
    
    def validate_prediction(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance prediction result"""
        # Check confidence threshold
        if result['confidence'] < self.confidence_threshold:
            result['warning'] = f"Low confidence ({result['confidence']:.2f}). Consider retaking the image."
        
        # Add confidence level description
        confidence = result['confidence']
        if confidence > 0.9:
            result['confidence_level'] = 'Very High'
        elif confidence > 0.8:
            result['confidence_level'] = 'High'
        elif confidence > 0.7:
            result['confidence_level'] = 'Good'
        elif confidence > 0.6:
            result['confidence_level'] = 'Fair'
        else:
            result['confidence_level'] = 'Low'
        
        # Add severity description
        severity_descriptions = {
            'high': 'Immediate attention required. Apply treatment as soon as possible.',
            'medium': 'Monitor closely and consider treatment options.',
            'low': 'Continue monitoring. Maintain good cultural practices.'
        }
        
        result['severity_description'] = severity_descriptions.get(
            result['severity'], 
            'Assessment unclear. Consult agricultural expert.'
        )
        
        return result
    
    def format_for_api(self, result: Dict[str, Any], 
                      processing_time: float = 0.0,
                      model_version: str = '1.0') -> Dict[str, Any]:
        """Format result for API response"""
        formatted = {
            'prediction': {
                'crop': result['crop'],
                'disease': result['disease'],
                'confidence': round(result['confidence'], 3),
                'confidence_level': result.get('confidence_level', 'Unknown'),
                'severity': result['severity'],
                'severity_description': result.get('severity_description', ''),
                'is_healthy': result.get('is_healthy', False),
                'requires_attention': result.get('requires_attention', True)
            },
            'treatments': result.get('treatments', []),
            'metadata': {
                'model_version': model_version,
                'processing_time': round(processing_time, 3),
                'timestamp': np.datetime64('now').isoformat(),
                'confidence_threshold': self.confidence_threshold
            }
        }
        
        # Add warnings if present
        if 'warning' in result:
            formatted['warning'] = result['warning']
        
        # Add all predictions if available
        if 'all_predictions' in result:
            formatted['alternative_predictions'] = result['all_predictions']
        
        # Add error if present
        if 'error' in result:
            formatted['error'] = result['error']
        
        return formatted