"""
mail.py – Standalone SMTP email helper for Vishudh Agro.

This module provides a reusable send_email() function using Python's
built-in smtplib, so no Flask-Mail dependency is required.

Usage:
    from utils.mail import send_email
    send_email(subject="Test", body="Hello")
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(subject: str, body: str) -> bool:
    """
    Send an email via SMTP using environment variables for configuration.

    Returns True on success, False on failure.
    """
    try:
        smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port     = int(os.getenv("SMTP_PORT", "587"))
        smtp_email    = os.getenv("SMTP_EMAIL", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        receiver      = os.getenv("RECEIVER_EMAIL", "")

        if not smtp_email or not smtp_password or not receiver:
            raise ValueError("SMTP configuration is incomplete. Check .env file.")

        msg = MIMEMultipart()
        msg["From"]    = smtp_email
        msg["To"]      = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print(f"[ERROR] send_email(): {e}")
        return False
