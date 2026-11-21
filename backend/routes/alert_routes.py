from flask import Blueprint, request, jsonify, render_template
from backend.authentication.auth_manager import login_required
from backend.services.alert_service import get_alert_service
from firebase.database_service import get_db_service

alert_bp = Blueprint("alerts", __name__)

@alert_bp.route("/api/alerts", methods=["POST"])
@login_required
def api_create_alert():
    user_id = request.current_user["user_id"]
    data = request.get_json() or {}
    alert_type = data.get("alert_type", "USER_MANUAL_ALERT")
    message = data.get("message", "User initiated health alert.")
    severity = data.get("severity", "medium")
    is_test = bool(data.get("is_test", False))

    alert_svc = get_alert_service()
    created = alert_svc.trigger_alert(
        user_id=user_id,
        alert_type=alert_type,
        message=message,
        severity=severity,
        is_test=is_test
    )

    if not created:
        return jsonify({"message": "Alert throttled / duplicate suppressed within 15-minute window."}), 200

    return jsonify({"message": "Alert generated successfully.", "alert": created}), 201

@alert_bp.route("/api/alerts", methods=["GET"])
@login_required
def api_get_alerts():
    user_id = request.current_user["user_id"]
    status = request.args.get("status")
    limit = request.args.get("limit", 50, type=int)

    db = get_db_service()
    alerts = db.get_alerts(user_id=user_id, status=status, limit=limit)
    return jsonify({"alerts": alerts, "count": len(alerts)}), 200

@alert_bp.route("/api/alerts/<alert_id>/resolve", methods=["PUT"])
@login_required
def api_resolve_alert(alert_id):
    db = get_db_service()
    updated = db.update_alert_status(alert_id, "resolved")
    if not updated:
        return jsonify({"error": "Alert not found."}), 404
    return jsonify({"message": "Alert resolved successfully.", "alert": updated}), 200

@alert_bp.route("/alerts", methods=["GET"])
@login_required
def alerts_page():
    user_id = request.current_user["user_id"]
    db = get_db_service()
    alerts = db.get_alerts(user_id=user_id, limit=50)
    return render_template("alerts.html", user=request.current_user, alerts=alerts)
