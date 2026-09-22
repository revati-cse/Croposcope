from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..services.treatment_service import get_treatment_recommendations

bp = Blueprint("treatments", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
def recommend():
    """
    Returns treatment recommendations for a given disease name.
    """
    data = request.get_json()
    disease = data.get("disease")
    if not disease:
        return jsonify({"msg": "Disease name required"}), 400

    try:
        recommendations = get_treatment_recommendations(disease)
        return jsonify({"disease": disease, "recommendations": recommendations})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
