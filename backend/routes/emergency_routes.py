from flask import Blueprint, request, jsonify, render_template
from backend.authentication.auth_manager import login_required
from backend.services.emergency_service import get_emergency_service

emergency_bp = Blueprint("emergency", __name__)

@emergency_bp.route("/api/emergency-contacts", methods=["GET"])
@login_required
def api_get_contacts():
    user_id = request.current_user["user_id"]
    svc = get_emergency_service()
    contacts = svc.get_contacts(user_id)
    return jsonify({"contacts": contacts}), 200

@emergency_bp.route("/api/emergency-contacts", methods=["POST"])
@login_required
def api_add_contact():
    user_id = request.current_user["user_id"]
    data = request.get_json() or {}
    svc = get_emergency_service()
    contact, status_code = svc.add_contact(user_id, data)
    return jsonify(contact), status_code

@emergency_bp.route("/api/emergency-contacts/<contact_id>", methods=["PUT"])
@login_required
def api_update_contact(contact_id):
    user_id = request.current_user["user_id"]
    data = request.get_json() or {}
    svc = get_emergency_service()
    res, status_code = svc.update_contact(contact_id, user_id, data)
    return jsonify(res), status_code

@emergency_bp.route("/api/emergency-contacts/<contact_id>", methods=["DELETE"])
@login_required
def api_delete_contact(contact_id):
    user_id = request.current_user["user_id"]
    svc = get_emergency_service()
    res, status_code = svc.delete_contact(contact_id, user_id)
    return jsonify(res), status_code

@emergency_bp.route("/api/emergency-contacts/test", methods=["POST"])
@login_required
def api_test_emergency():
    user_id = request.current_user["user_id"]
    svc = get_emergency_service()
    res, status_code = svc.trigger_test_emergency(user_id)
    return jsonify(res), status_code

@emergency_bp.route("/emergency-contacts", methods=["GET"])
@login_required
def emergency_contacts_page():
    user_id = request.current_user["user_id"]
    svc = get_emergency_service()
    contacts = svc.get_contacts(user_id)
    return render_template("emergency_contacts.html", user=request.current_user, contacts=contacts)
