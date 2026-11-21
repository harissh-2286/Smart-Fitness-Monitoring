import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import Config

logger = logging.getLogger("SmartFitness.EmailService")

def send_email_alert(recipient_email, subject, message_html, message_plain=None, is_test=False):
    """
    Sends email alert via SMTP or logs simulation when SMTP is not configured.
    Returns: dict(status="SENT"|"SIMULATED"|"FAILED", details=str)
    """
    if not recipient_email:
        return {"status": "FAILED", "details": "Recipient email address is missing."}

    if is_test:
        subject = f"[TEST NOTIFICATION] {subject}"

    if not Config.SMTP_ENABLED or not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD or Config.SMTP_PASSWORD == "mock_password":
        logger.info(
            f"[EMAIL SIMULATION] Mode: Active. Recipient: {recipient_email}. "
            f"Subject: '{subject}'. Body Preview: {message_plain or message_html[:80]}..."
        )
        return {
            "status": "SIMULATED",
            "channel": "email",
            "recipient": recipient_email,
            "subject": subject,
            "details": "Email simulated successfully (SMTP disabled or credentials in demo mode)."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.SMTP_FROM_EMAIL
        msg["To"] = recipient_email

        if message_plain:
            msg.attach(MIMEText(message_plain, "plain"))
        if message_html:
            msg.attach(MIMEText(message_html, "html"))

        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_FROM_EMAIL, recipient_email, msg.as_string())

        logger.info(f"Email successfully delivered to {recipient_email}")
        return {
            "status": "SENT",
            "channel": "email",
            "recipient": recipient_email,
            "subject": subject,
            "details": f"Dispatched via SMTP {Config.SMTP_SERVER}:{Config.SMTP_PORT}"
        }
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return {
            "status": "FAILED",
            "channel": "email",
            "recipient": recipient_email,
            "details": str(e)
        }
