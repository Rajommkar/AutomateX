from __future__ import annotations

import smtplib
from email.message import EmailMessage


def send_email(
    email_settings: dict,
    subject: str,
    body: str,
    recipient: str | None = None,
    logger=None,
    dry_run: bool = False,
) -> dict:
    sender = email_settings.get("sender_email", "")
    password = email_settings.get("sender_password", "")
    smtp_server = email_settings.get("smtp_server", "")
    smtp_port = int(email_settings.get("smtp_port", 587))
    use_tls = bool(email_settings.get("use_tls", True))
    target_recipient = recipient or email_settings.get("recipient_email", "")

    if not target_recipient:
        raise ValueError("Recipient email is required.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender or "not-configured@example.com"
    message["To"] = target_recipient
    message.set_content(body)

    result = {
        "recipient": target_recipient,
        "subject": subject,
        "status": "dry_run" if dry_run else "sent",
    }

    if dry_run:
        if logger:
            logger.info("Dry-run email prepared for %s with subject '%s'", target_recipient, subject)
        return result

    if not all([sender, password, smtp_server]):
        raise ValueError(
            "Email settings are incomplete. Update sender_email, sender_password, and smtp_server."
        )

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
        if use_tls:
            server.starttls()
        server.login(sender, password)
        server.send_message(message)

    if logger:
        logger.info("Email sent to %s with subject '%s'", target_recipient, subject)

    return result
