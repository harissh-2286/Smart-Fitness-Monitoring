from flask import Blueprint, request, jsonify, render_template
from backend.authentication.auth_manager import login_required
from backend.services.analytics_service import get_analytics_service
from firebase.database_service import get_db_service

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/api/analytics", methods=["GET"])
@login_required
def api_get_analytics():
    user_id = request.current_user["user_id"]
    analytics_svc = get_analytics_service()
    analytics_data = analytics_svc.compute_user_analytics(user_id)
    return jsonify(analytics_data), 200

@analytics_bp.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    data = request.get_json() or {}
    heart_rate = data.get("heart_rate")
    step_cadence = data.get("step_cadence", 0)
    accel_magnitude = data.get("accel_magnitude", 9.8)
    speed_kmh = data.get("speed_kmh", 0.0)

    if heart_rate is None:
        return jsonify({"error": "heart_rate is required for machine learning prediction."}), 400

    analytics_svc = get_analytics_service()
    prediction = analytics_svc.predict_activity_and_anomaly(
        heart_rate=heart_rate,
        step_cadence=step_cadence,
        accel_magnitude=accel_magnitude,
        speed_kmh=speed_kmh
    )

    return jsonify({"prediction": prediction}), 200

@analytics_bp.route("/api/predictions", methods=["GET"])
@login_required
def api_get_predictions():
    user_id = request.current_user["user_id"]
    db = get_db_service()
    history = db.get_analytics_history(user_id, limit=30)
    return jsonify({"history": history}), 200

@analytics_bp.route("/analytics", methods=["GET"])
@login_required
def analytics_page():
    user_id = request.current_user["user_id"]
    analytics_svc = get_analytics_service()
    analytics_data = analytics_svc.compute_user_analytics(user_id)
    return render_template("analytics.html", user=request.current_user, analytics=analytics_data)
