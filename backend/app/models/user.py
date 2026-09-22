from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200))
    preferences = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    analyses = db.relationship('CropAnalysis', backref='user', lazy=True)
    fields = db.relationship('Field', backref='user', lazy=True)
    voice_interactions = db.relationship('VoiceInteraction', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_preferences(self, preferences_dict):
        self.preferences = json.dumps(preferences_dict)
    
    def get_preferences(self):
        if self.preferences:
            return json.loads(self.preferences)
        return {"language": "en", "theme": "system", "notifications": True}
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'avatar': self.avatar,
            'preferences': self.get_preferences(),
            'created_at': self.created_at.isoformat()
        }

class CropAnalysis(db.Model):
    __tablename__ = 'crop_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    crop_type = db.Column(db.String(100), nullable=False)
    disease_detected = db.Column(db.String(200), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    severity_level = db.Column(db.Enum('low', 'medium', 'high', name='severity_levels'), nullable=False)
    field_location = db.Column(db.String(200))
    treatment_applied = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    model_version = db.Column(db.String(50), default='efficientnetv2-1.0')
    processing_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_type': self.crop_type,
            'disease_detected': self.disease_detected,
            'confidence_score': self.confidence_score,
            'severity_level': self.severity_level,
            'field_location': self.field_location,
            'treatment_applied': self.treatment_applied,
            'notes': self.notes,
            'model_version': self.model_version,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'image_path': self.image_path
        }

class Treatment(db.Model):
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    disease_target = db.Column(db.String(200), nullable=False)
    crop_target = db.Column(db.String(200), nullable=False)
    treatment_type = db.Column(db.Enum('organic', 'biological', 'cultural', 'preventive', name='treatment_types'), nullable=False)
    effectiveness_rating = db.Column(db.Integer)  # 1-100
    duration = db.Column(db.String(100))
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard', name='difficulty_levels'), nullable=False)
    ingredients = db.Column(db.Text)  # JSON array
    instructions = db.Column(db.Text)  # JSON array
    benefits = db.Column(db.Text)  # JSON array
    precautions = db.Column(db.Text)  # JSON array
    cost_level = db.Column(db.Enum('low', 'medium', 'high', name='cost_levels'), nullable=False)
    seasonal_info = db.Column(db.Text)  # JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'disease_target': self.disease_target,
            'crop_target': self.crop_target,
            'treatment_type': self.treatment_type,
            'effectiveness_rating': self.effectiveness_rating,
            'duration': self.duration,
            'difficulty_level': self.difficulty_level,
            'ingredients': json.loads(self.ingredients) if self.ingredients else [],
            'instructions': json.loads(self.instructions) if self.instructions else [],
            'benefits': json.loads(self.benefits) if self.benefits else [],
            'precautions': json.loads(self.precautions) if self.precautions else [],
            'cost_level': self.cost_level,
            'seasonal_info': json.loads(self.seasonal_info) if self.seasonal_info else [],
            'created_at': self.created_at.isoformat()
        }

class Field(db.Model):
    __tablename__ = 'fields'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(500))
    size_acres = db.Column(db.Float)
    soil_type = db.Column(db.String(100))
    current_crop = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VoiceInteraction(db.Model):
    __tablename__ = 'voice_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transcript = db.Column(db.Text, nullable=False)
    language_code = db.Column(db.String(10), nullable=False)
    command_type = db.Column(db.String(100))
    response_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)