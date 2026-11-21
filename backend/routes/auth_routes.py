from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from backend.authentication.auth_manager import auth_manager, login_required
from firebase.database_service import get_db_service

auth_bp = Blueprint("auth", __name__)

# ================= API ENDPOINTS =================

@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    res, status_code = auth_manager.register_user(data)
    if status_code == 201:
        # Also store token in session for web browser ease
        session["jwt_token"] = res["token"]
        session["user_id"] = res["user"]["user_id"]
    return jsonify(res), status_code

@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    res, status_code = auth_manager.login_user(email, password)
    if status_code == 200:
        session["jwt_token"] = res["token"]
        session["user_id"] = res["user"]["user_id"]
    return jsonify(res), status_code

@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Successfully logged out."}), 200

@auth_bp.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    db = get_db_service()
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({"error": "No account found with this email."}), 404

    # Simulate email recovery dispatch
    from notifications.email_service import send_email_alert
    send_email_alert(
        recipient_email=email,
        subject="Password Reset Instructions - Smart Fitness",
        message_html=f"<p>Hello {user.get('name')},</p><p>A password reset request was initiated for your Smart Fitness account.</p>",
        message_plain="A password reset request was initiated for your Smart Fitness account.",
        is_test=True
    )
    return jsonify({"message": f"Password reset instructions sent to {email}."}), 200

@auth_bp.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    new_password = data.get("new_password", "")

    if not email or not new_password or len(new_password) < 6:
        return jsonify({"error": "Valid email and new password (min 6 chars) required."}), 400

    db = get_db_service()
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User account not found."}), 404

    new_hash = auth_manager.hash_password(new_password)
    db.update_user(user["user_id"], {"password_hash": new_hash})
    return jsonify({"message": "Password updated successfully."}), 200

@auth_bp.route("/api/profile", methods=["GET"])
@login_required
def api_get_profile():
    user = request.current_user
    return jsonify({"user": user}), 200

@auth_bp.route("/api/profile", methods=["PUT"])
@login_required
def api_update_profile():
    user_id = request.current_user["user_id"]
    data = request.get_json() or {}
    
    # Filter editable fields
    editable_fields = ["name", "age", "height", "weight", "gender", "step_goal", "calorie_goal", "sleep_goal"]
    updates = {}
    for f in editable_fields:
        if f in data:
            if f in ["age", "step_goal", "calorie_goal"]:
                updates[f] = int(data[f])
            elif f in ["height", "weight", "sleep_goal"]:
                updates[f] = float(data[f])
            else:
                updates[f] = data[f]

    db = get_db_service()
    updated_user = db.update_user(user_id, updates)
    if not updated_user:
        return jsonify({"error": "Failed to update profile."}), 500

    safe_user = {k: v for k, v in updated_user.items() if k != "password_hash"}
    return jsonify({"message": "Profile updated successfully.", "user": safe_user}), 200

# ================= WEB VIEWS =================

@auth_bp.route("/login", methods=["GET"])
def login_page():
    if auth_manager.get_current_user_from_request():
        return redirect(url_for("health.dashboard_page"))
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET"])
def register_page():
    if auth_manager.get_current_user_from_request():
        return redirect(url_for("health.dashboard_page"))
    return render_template("register.html")

@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    return render_template("forgot_password.html")

@auth_bp.route("/reset-password", methods=["GET"])
def reset_password_page():
    return render_template("reset_password.html")

@auth_bp.route("/logout", methods=["GET"])
def logout_view():
    session.clear()
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile_page():
    return render_template("profile.html", user=request.current_user)
