import logging
from backend.config import Config

logger = logging.getLogger("SmartFitness.SMSService")

def send_sms_alert(phone_number, message, is_test=False):
    """
    Dispatches SMS alert via Twilio REST API or provides mock simulation
    when Twilio credentials are not configured.
    Returns: dict(status="SENT"|"SIMULATED"|"FAILED", details=str)
    """
    if not phone_number:
        return {"status": "FAILED", "details": "Recipient phone number is missing."}

    if is_test:
        message = f"[TEST ALERT] {message}"

    if not Config.TWILIO_ENABLED or not Config.TWILIO_ACCOUNT_SID or Config.TWILIO_ACCOUNT_SID == "mock_sid":
        logger.info(
            f"[SMS SIMULATION] Mode: Active. Recipient: {phone_number}. "
            f"Message: {message}"
        )
        return {
            "status": "SIMULATED",
            "channel": "sms",
            "recipient": phone_number,
            "message": message,
            "details": "SMS simulated successfully (Twilio disabled or in demo mode)."
        }

    try:
        from twilio.rest import Client
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        sent_msg = client.messages.create(
            body=message,
            from_=Config.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"SMS successfully dispatched to {phone_number}, SID: {sent_msg.sid}")
        return {
            "status": "SENT",
            "channel": "sms",
            "recipient": phone_number,
            "sid": sent_msg.sid,
            "details": "Dispatched via Twilio API."
        }
    except Exception as e:
        logger.error(f"Failed to send Twilio SMS to {phone_number}: {e}")
        return {
            "status": "FAILED",
            "channel": "sms",
            "recipient": phone_number,
            "details": str(e)
        }
