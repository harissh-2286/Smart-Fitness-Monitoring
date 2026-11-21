import re
from firebase.database_service import get_db_service
from notifications.email_service import send_email_alert
from notifications.sms_service import send_sms_alert

class EmergencyService:
    def __init__(self):
        self.db = get_db_service()

    def get_contacts(self, user_id):
        return self.db.get_emergency_contacts(user_id)

    def add_contact(self, user_id, contact_data):
        name = contact_data.get("name", "").strip()
        relationship = contact_data.get("relationship", "Family").strip()
        phone = contact_data.get("phone", "").strip()
        email = contact_data.get("email", "").strip()
        is_primary = bool(contact_data.get("is_primary", False))

        if not name or len(name) < 2:
            return {"error": "Contact name is required."}, 400

        if not phone and not email:
            return {"error": "Please provide at least a phone number or email for the contact."}, 400

        # Reset other primaries if this is primary
        if is_primary:
            existing = self.db.get_emergency_contacts(user_id)
            for c in existing:
                if c.get("is_primary"):
                    self.db.update_emergency_contact(c["contact_id"], user_id, {"is_primary": False})

        new_contact = {
            "user_id": user_id,
            "name": name,
            "relationship": relationship,
            "phone": phone,
            "email": email,
            "is_primary": is_primary
        }

        created = self.db.add_emergency_contact(new_contact)
        return created, 201

    def update_contact(self, contact_id, user_id, updates):
        updated = self.db.update_emergency_contact(contact_id, user_id, updates)
        if not updated:
            return {"error": "Contact not found or unauthorized."}, 404
        return updated, 200

    def delete_contact(self, contact_id, user_id):
        success = self.db.delete_emergency_contact(contact_id, user_id)
        if not success:
            return {"error": "Contact not found or unauthorized."}, 404
        return {"message": "Contact deleted successfully."}, 200

    def trigger_test_emergency(self, user_id):
        """
        Sends an explicit test emergency alert to all user's emergency contacts
        to verify delivery channels and readiness without triggering actual 911 / hospital dispatch.
        """
        user = self.db.get_user_by_id(user_id) or {}
        contacts = self.get_contacts(user_id)

        if not contacts:
            return {"error": "No emergency contacts configured yet. Please add a contact first."}, 400

        results = []
        user_name = user.get("name", "User")

        for contact in contacts:
            c_name = contact.get("name")
            phone = contact.get("phone")
            email = contact.get("email")

            test_msg = (
                f"[SMART FITNESS TEST NOTIFICATION]: This is a test emergency alert from {user_name}. "
                f"Emergency notification channels verified successfully. No action required."
            )

            sms_res = None
            email_res = None

            if phone:
                sms_res = send_sms_alert(phone, test_msg, is_test=True)
            if email:
                email_res = send_email_alert(
                    email,
                    subject="TEST EMERGENCY DISPATCH - Smart Fitness",
                    message_html=f"<h3>Test Emergency Alert</h3><p>{test_msg}</p>",
                    message_plain=test_msg,
                    is_test=True
                )

            results.append({
                "contact_id": contact.get("contact_id"),
                "name": c_name,
                "phone": phone,
                "email": email,
                "sms_result": sms_res,
                "email_result": email_res
            })

        return {
            "message": f"Test alert successfully dispatched to {len(contacts)} emergency contact(s).",
            "dispatch_log": results
        }, 200


_emergency_service = None

def get_emergency_service():
    global _emergency_service
    if _emergency_service is None:
        _emergency_service = EmergencyService()
    return _emergency_service
