from flask import Blueprint, request, jsonify, render_template
from backend.authentication.auth_manager import admin_required
from firebase.database_service import get_db_service

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/admin/overview", methods=["GET"])
@admin_required
def api_admin_overview():
    db = get_db_service()
    stats = db.get_aggregate_stats()
    return jsonify(stats), 200

@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_required
def api_admin_users():
    db = get_db_service()
    users = db.list_all_users()
    # Mask passwords
    safe_users = [{k: v for k, v in u.items() if k != "password_hash"} for u in users]
    return jsonify({"users": safe_users}), 200

@admin_bp.route("/api/admin/alerts", methods=["GET"])
@admin_required
def api_admin_alerts():
    db = get_db_service()
    alerts = db.get_alerts(limit=100)
    return jsonify({"alerts": alerts}), 200

@admin_bp.route("/admin", methods=["GET"])
@admin_required
def admin_page():
    db = get_db_service()
    stats = db.get_aggregate_stats()
    users = db.list_all_users()
    safe_users = [{k: v for k, v in u.items() if k != "password_hash"} for u in users]
    recent_alerts = db.get_alerts(limit=25)
    return render_template(
        "admin.html",
        user=request.current_user,
        stats=stats,
        users=safe_users,
        alerts=recent_alerts
    )
