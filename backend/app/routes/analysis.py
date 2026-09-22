from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import time
from app import db
from app.models.user import CropAnalysis
from app.ml_model.disease_detector import CropDiseaseDetector

analysis_bp = Blueprint('analysis', __name__)

# Initialize ML model
detector = CropDiseaseDetector()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@analysis_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_and_analyze():
    """Upload image and analyze for crop disease"""
    try:
        user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{user_id}_{timestamp}_{filename}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get additional data from form
            crop_type = request.form.get('crop_type', 'Unknown')
            field_location = request.form.get('field_location', '')
            notes = request.form.get('notes', '')
            
            # Analyze image with ML model
            prediction_result = detector.predict_disease(filepath)
            
            if 'error' in prediction_result:
                return jsonify({'error': prediction_result['error']}), 500
            
            # Save analysis to database
            analysis = CropAnalysis(
                user_id=user_id,
                image_path=filepath,
                crop_type=prediction_result.get('crop', crop_type),
                disease_detected=prediction_result['disease'],
                confidence_score=prediction_result['confidence'],
                severity_level=prediction_result['severity'],
                field_location=field_location,
                notes=notes,
                model_version=prediction_result.get('model_version', 'efficientnetv2-1.0'),
                processing_time=prediction_result.get('processing_time', 0)
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            # Return analysis result
            return jsonify({
                'analysis_id': analysis.id,
                'crop': prediction_result['crop'],
                'disease': prediction_result['disease'],
                'confidence': prediction_result['confidence'],
                'severity': prediction_result['severity'],
                'processing_time': prediction_result.get('processing_time', 0),
                'model_version': prediction_result.get('model_version'),
                'all_predictions': prediction_result.get('all_predictions', []),
                'created_at': analysis.created_at.isoformat()
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    """Get user's analysis history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        analyses = CropAnalysis.query.filter_by(user_id=user_id)\
                                   .order_by(CropAnalysis.created_at.desc())\
                                   .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        user_id = get_jwt_identity()
        
        analysis = CropAnalysis.query.filter_by(
            id=analysis_id, 
            user_id=user_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/<int:analysis_id>/treatment', methods=['PUT'])
@jwt_required()
def update_treatment_status(analysis_id):
    """Update treatment status for an analysis"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        analysis = CropAnalysis.query.filter_by(
            id=analysis_id, 
            user_id=user_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        analysis.treatment_applied = data.get('treatment_applied', False)
        if 'notes' in data:
            analysis.notes = data['notes']
        
        db.session.commit()
        
        return jsonify(analysis.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get analytics data for user's analyses"""
    try:
        user_id = get_jwt_identity()
        
        # Get all user analyses
        analyses = CropAnalysis.query.filter_by(user_id=user_id).all()
        
        total_analyses = len(analyses)
        if total_analyses == 0:
            return jsonify({
                'total_analyses': 0,
                'disease_detected': 0,
                'average_confidence': 0,
                'treatment_compliance': 0,
                'disease_distribution': {},
                'crop_distribution': {},
                'severity_distribution': {}
            })
        
        # Calculate statistics
        diseases_detected = [a for a in analyses if 'healthy' not in a.disease_detected.lower()]
        disease_count = len(diseases_detected)
        
        avg_confidence = sum(a.confidence_score for a in analyses) / total_analyses
        
        treatments_applied = sum(1 for a in analyses if a.treatment_applied)
        treatment_compliance = (treatments_applied / total_analyses) * 100
        
        # Distribution statistics
        disease_dist = {}
        crop_dist = {}
        severity_dist = {}
        
        for analysis in analyses:
            # Disease distribution
            disease = analysis.disease_detected
            disease_dist[disease] = disease_dist.get(disease, 0) + 1
            
            # Crop distribution
            crop = analysis.crop_type
            crop_dist[crop] = crop_dist.get(crop, 0) + 1
            
            # Severity distribution
            severity = analysis.severity_level
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
        
        return jsonify({
            'total_analyses': total_analyses,
            'disease_detected': disease_count,
            'average_confidence': round(avg_confidence, 2),
            'treatment_compliance': round(treatment_compliance, 2),
            'disease_distribution': disease_dist,
            'crop_distribution': crop_dist,
            'severity_distribution': severity_dist
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500