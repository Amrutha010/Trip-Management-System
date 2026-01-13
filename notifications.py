import os
import smtplib
from email.message import EmailMessage

def notify_agent_approval(user, approved: bool):
    """
    Notify agent by email (if SMTP configured) or print to console.
    Expects user to have .username and optionally .email attribute (not required).
    Configure SMTP via env vars: SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
    """
    subject = "Agent account " + ("approved" if approved else "rejected")
    body = f"Hello {user.username},\n\nYour agent account has been {'approved' if approved else 'rejected'}.\n\nThanks,\nTrip Management System"
    print(f"[notify] {subject} -> {user.username}")
    # attempt email if env configured
    server = os.environ.get("SMTP_SERVER")
    if not server:
        print("SMTP not configured; skipping email send.")
        return
    try:
        port = int(os.environ.get("SMTP_PORT", "587"))
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = os.environ.get("FROM_EMAIL", "noreply@example.com")
        msg["To"] = getattr(user, "email", user.username)
        msg.set_content(body)
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS"))
            smtp.send_message(msg)
        print("Email notification sent.")
    except Exception as e:
        print("Failed to send email:", e)