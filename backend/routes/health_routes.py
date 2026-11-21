from flask import Blueprint, request, jsonify, render_template
from backend.authentication.auth_manager import login_required
from backend.services.health_service import get_health_service
from backend.services.analytics_service import get_analytics_service
from backend.services.alert_service import get_alert_service
from firebase.database_service import get_db_service

health_bp = Blueprint("health", __name__)

# ================= API ENDPOINTS =================

@health_bp.route("/api/health-data", methods=["POST"])
@login_required
def api_add_health_data():
    user_id = request.current_user["user_id"]
    data = request.get_json() or {}
    
    health_svc = get_health_service()
    record, status_code = health_svc.record_health_data(user_id, data)
    if status_code != 201:
        return jsonify(record), status_code

    # Real-time intelligent evaluation: trigger ML inference and check health alert rules
    analytics_svc = get_analytics_service()
    alert_svc = get_alert_service()

    ml_res = None
    if record.get("heart_rate") is not None:
        step_cadence = min(180, int((record.get("steps") or 0) / 60))
        ml_res = analytics_svc.predict_activity_and_anomaly(
            heart_rate=record["heart_rate"],
            step_cadence=step_cadence
        )

    # Evaluate health reading for clinical thresholds & anomalies
    triggered_alerts = alert_svc.evaluate_health_reading(user_id, record, ml_res)

    return jsonify({
        "message": "Health data recorded successfully.",
        "record": record,
        "ml_inference": ml_res,
        "alerts_triggered": triggered_alerts
    }), 201

@health_bp.route("/api/health-data", methods=["GET"])
@login_required
def api_get_health_data():
    user_id = request.current_user["user_id"]
    limit = request.args.get("limit", 50, type=int)
    db = get_db_service()
    records = db.get_health_records(user_id, limit=limit)
    return jsonify({"records": records, "count": len(records)}), 200

@health_bp.route("/api/dashboard", methods=["GET"])
@login_required
def api_get_dashboard():
    user_id = request.current_user["user_id"]
    health_svc = get_health_service()
    summary = health_svc.get_dashboard_summary(user_id)
    return jsonify(summary), 200

# ================= WEB VIEWS =================

@health_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard_page():
    health_svc = get_health_service()
    data = health_svc.get_dashboard_summary(request.current_user["user_id"])
    return render_template("dashboard.html", user=request.current_user, data=data)

@health_bp.route("/heart-rate", methods=["GET"])
@login_required
def heart_rate_page():
    user_id = request.current_user["user_id"]
    db = get_db_service()
    records = db.get_health_records(user_id, limit=100)
    return render_template("heart_rate.html", user=request.current_user, records=records)

@health_bp.route("/activity", methods=["GET"])
@login_required
def activity_page():
    user_id = request.current_user["user_id"]
    health_svc = get_health_service()
    data = health_svc.get_dashboard_summary(user_id)
    return render_template("activity.html", user=request.current_user, data=data)

@health_bp.route("/sleep", methods=["GET"])
@login_required
def sleep_page():
    user_id = request.current_user["user_id"]
    db = get_db_service()
    records = [r for r in db.get_health_records(user_id, limit=100) if r.get("sleep_hours") is not None]
    return render_template("sleep.html", user=request.current_user, records=records)
