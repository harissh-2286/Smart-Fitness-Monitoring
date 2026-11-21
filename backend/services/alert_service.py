import datetime
from datetime import timezone, timedelta
import logging
from backend.config import Config
from firebase.database_service import get_db_service
from notifications.email_service import send_email_alert
from notifications.sms_service import send_sms_alert
from notifications.push_service import send_push_alert

logger = logging.getLogger("SmartFitness.AlertService")

class AlertService:
    def __init__(self):
        self.db = get_db_service()

    def evaluate_health_reading(self, user_id, reading_data, ml_result=None):
        """
        Intelligent alert engine that monitors:
        - Heart Rate Anomaly (Bradycardia, Tachycardia, Sudden Spike)
        - ML Isolation Forest Anomaly
        - Activity Goals / Inactivity
        - Sleep Quality
        Debounces duplicate alerts within a 15-minute window.
        """
        generated_alerts = []
        user = self.db.get_user_by_id(user_id) or {}
        heart_rate = reading_data.get("heart_rate")
        steps = reading_data.get("steps")
        sleep_hours = reading_data.get("sleep_hours")
        activity_type = reading_data.get("activity_type", "Resting")
        is_demo = reading_data.get("data_source") == "demo"

        # 1. Heart Rate Evaluation
        if heart_rate is not None:
            hr = float(heart_rate)
            # Tachycardia check
            if hr > 115 and activity_type == "Resting":
                alert = self.trigger_alert(
                    user_id=user_id,
                    alert_type="TACHYCARDIA_RESTING",
                    message=f"Elevated resting heart rate detected ({int(hr)} BPM). Please sit down, rest, and hydrate.",
                    severity="high",
                    is_test=is_demo
                )
                if alert: generated_alerts.append(alert)

            # Bradycardia check
            elif hr < 48:
                alert = self.trigger_alert(
                    user_id=user_id,
                    alert_type="BRADYCARDIA_LOW_HR",
                    message=f"Abnormally low heart rate detected ({int(hr)} BPM).",
                    severity="high",
                    is_test=is_demo
                )
                if alert: generated_alerts.append(alert)

            # Extreme Exercise Threshold
            elif hr > 185:
                alert = self.trigger_alert(
                    user_id=user_id,
                    alert_type="MAX_HEART_RATE_EXCEEDED",
                    message=f"Heart rate reached peak zone ({int(hr)} BPM). Reduce workout intensity immediately.",
                    severity="critical",
                    is_test=is_demo
                )
                if alert: generated_alerts.append(alert)

        # 2. Machine Learning Anomaly Detection
        if ml_result and ml_result.get("is_anomaly"):
            risk = ml_result.get("risk_indicator", "Moderate Risk")
            sev = "critical" if risk == "High Risk" else "high"
            alert = self.trigger_alert(
                user_id=user_id,
                alert_type="ML_PHYSIOLOGICAL_ANOMALY",
                message=f"Machine Learning Anomaly Detector flagged irregular physiological pattern (Risk: {risk}).",
                severity=sev,
                is_test=is_demo
            )
            if alert: generated_alerts.append(alert)

        # 3. Step Goal Achievement
        if steps is not None:
            step_goal = user.get("step_goal", 10000)
            if steps >= step_goal:
                alert = self.trigger_alert(
                    user_id=user_id,
                    alert_type="GOAL_ACHIEVEMENT",
                    message=f"Congratulations! You reached your daily goal of {step_goal:,} steps today!",
                    severity="info",
                    is_test=is_demo
                )
                if alert: generated_alerts.append(alert)

        # 4. Sleep Alert
        if sleep_hours is not None:
            if sleep_hours < 5.0:
                alert = self.trigger_alert(
                    user_id=user_id,
                    alert_type="INSUFFICIENT_SLEEP",
                    message=f"Insufficient sleep duration logged ({sleep_hours} hrs). Chronic sleep deficit impacts recovery and cardiac health.",
                    severity="medium",
                    is_test=is_demo
                )
                if alert: generated_alerts.append(alert)

        return generated_alerts

    def trigger_alert(self, user_id, alert_type, message, severity="medium", is_test=False):
        """
        Applies duplicate suppression (15-min debounce) and dispatches notifications.
        """
        # Duplicate prevention check
        recent_alerts = self.db.get_alerts(user_id=user_id, limit=10)
        now = datetime.datetime.now(timezone.utc)
        debounce_window = timedelta(minutes=15)

        for a in recent_alerts:
            if a.get("alert_type") == alert_type:
                t_str = a.get("timestamp")
                if t_str:
                    try:
                        t = datetime.datetime.fromisoformat(t_str)
                        if now - t < debounce_window:
                            logger.info(f"Duplicate alert {alert_type} suppressed for user {user_id} within debounce window.")
                            return None
                    except Exception:
                        pass

        alert_record = {
            "user_id": user_id,
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "status": "active",
            "is_test": is_test,
            "timestamp": now.isoformat(),
            "notification_status": {}
        }

        # 1. Dispatch Web Push notification
        push_res = send_push_alert(
            user_id=user_id,
            title=f"Health Alert: {alert_type.replace('_', ' ').title()}",
            body=message,
            severity=severity,
            is_test=is_test
        )
        alert_record["notification_status"]["push"] = push_res.get("status", "DELIVERED")

        # 2. If High or Critical, dispatch Email & SMS to user and emergency contacts
        user = self.db.get_user_by_id(user_id) or {}
        user_email = user.get("email")

        if severity in ["high", "critical"] and user_email:
            email_res = send_email_alert(
                recipient_email=user_email,
                subject=f"URGENT HEALTH ALERT: {alert_type}",
                message_html=f"<h3>Health Monitoring Alert</h3><p>{message}</p><p>Severity: <b>{severity.upper()}</b></p>",
                message_plain=message,
                is_test=is_test
            )
            alert_record["notification_status"]["email"] = email_res.get("status")

        # 3. If Critical, escalate to Emergency Contacts!
        if severity == "critical":
            contacts = self.db.get_emergency_contacts(user_id)
            escalated_count = 0
            for contact in contacts:
                contact_email = contact.get("email")
                contact_phone = contact.get("phone")
                c_name = contact.get("name", "Emergency Contact")
                escalation_msg = (
                    f"EMERGENCY HEALTH ALERT: Your contact {user.get('name', 'User')} "
                    f"triggered a critical health alert: '{message}'. Time: {now.strftime('%H:%M:%S UTC')}."
                )

                if contact_email:
                    send_email_alert(
                        recipient_email=contact_email,
                        subject=f"CRITICAL HEALTH NOTIFICATION FOR {user.get('name', 'User')}",
                        message_html=f"<p>{escalation_msg}</p>",
                        message_plain=escalation_msg,
                        is_test=is_test
                    )
                if contact_phone:
                    send_sms_alert(
                        phone_number=contact_phone,
                        message=escalation_msg,
                        is_test=is_test
                    )
                escalated_count += 1
            alert_record["notification_status"]["emergency_escalated"] = escalated_count

        saved_alert = self.db.create_alert(alert_record)
        return saved_alert


_alert_service = None

def get_alert_service():
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
