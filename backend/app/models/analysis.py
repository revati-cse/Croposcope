from .. import db
from datetime import datetime


class CropAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    result = db.Column(db.String(200), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
