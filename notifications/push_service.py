import logging
from datetime import datetime, timezone

logger = logging.getLogger("SmartFitness.PushService")

def send_push_alert(user_id, title, body, severity="medium", data=None, is_test=False):
    """
    Simulates Firebase Cloud Messaging (FCM) / Web Push notifications.
    In browser, notifications are reflected in the in-app notification center
    and dispatched through Web Notification API when granted.
    """
    if is_test:
        title = f"[TEST] {title}"

    push_payload = {
        "user_id": user_id,
        "title": title,
        "body": body,
        "severity": severity,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "DELIVERED",
        "channel": "web_push"
    }

    logger.info(f"[PUSH NOTIFICATION] User: {user_id} | Title: {title} | Severity: {severity}")
    return push_payload
