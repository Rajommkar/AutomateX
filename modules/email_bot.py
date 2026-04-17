from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr


ENV_MAPPING = {
    "sender_email": "AUTOMATEX_SENDER_EMAIL",
    "sender_password": "AUTOMATEX_SENDER_PASSWORD",
    "recipient_email": "AUTOMATEX_RECIPIENT_EMAIL",
    "smtp_server": "AUTOMATEX_SMTP_SERVER",
    "smtp_port": "AUTOMATEX_SMTP_PORT",
    "use_tls": "AUTOMATEX_USE_TLS",
}


def _read_email_settings(email_settings: dict) -> dict:
    resolved_settings = dict(email_settings)

    for key, env_name in ENV_MAPPING.items():
        env_value = os.getenv(env_name)
        if env_value in (None, ""):
            continue

        if key == "smtp_port":
            resolved_settings[key] = int(env_value)
        elif key == "use_tls":
            resolved_settings[key] = env_value.strip().lower() in {"1", "true", "yes", "on"}
        else:
            resolved_settings[key] = env_value

    return resolved_settings


def _is_valid_email(value: str) -> bool:
    _, parsed_email = parseaddr(value)
    return bool(parsed_email) and "@" in parsed_email and "." in parsed_email.rsplit("@", 1)[-1]


def _validate_email_input(subject: str, body: str, recipient: str) -> None:
    if not subject or not subject.strip():
        raise ValueError("Email subject is required.")

    if not body or not body.strip():
        raise ValueError("Email message body is required.")

    if not _is_valid_email(recipient):
        raise ValueError("Recipient email is not valid.")


def send_email(
    email_settings: dict,
    subject: str,
    body: str,
    recipient: str | None = None,
    logger=None,
    dry_run: bool = False,
) -> dict:
    resolved_settings = _read_email_settings(email_settings)
    sender = resolved_settings.get("sender_email", "")
    password = resolved_settings.get("sender_password", "")
    smtp_server = resolved_settings.get("smtp_server", "")
    smtp_port = int(resolved_settings.get("smtp_port", 587))
    use_tls = bool(resolved_settings.get("use_tls", True))
    target_recipient = recipient or resolved_settings.get("recipient_email", "")

    if not target_recipient:
        raise ValueError("Recipient email is required.")

    _validate_email_input(subject, body, target_recipient)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender or "not-configured@example.com"
    message["To"] = target_recipient
    message.set_content(body)

    result = {
        "recipient": target_recipient,
        "subject": subject,
        "status": "dry_run" if dry_run else "sent",
        "delivery_mode": "dry_run" if dry_run else "smtp",
        "message": "Email validated in dry-run mode." if dry_run else "",
    }

    if dry_run:
        if logger:
            logger.info(
                "Dry-run email prepared for %s with subject '%s'",
                target_recipient,
                subject,
            )
        return result

    if not all([sender, password, smtp_server]):
        raise ValueError(
            "Email settings are incomplete. Configure credentials in environment variables or settings.json."
        )

    if not _is_valid_email(sender):
        raise ValueError("Sender email is not valid.")

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            if use_tls:
                server.starttls()
            server.login(sender, password)
            server.send_message(message)
    except (smtplib.SMTPException, OSError) as error:
        if logger:
            logger.error(
                "Email delivery failed for %s with subject '%s' | %s",
                target_recipient,
                subject,
                error,
            )
        raise RuntimeError(f"Email delivery failed: {error}") from error

    result["message"] = "Email sent successfully."

    if logger:
        logger.info("Email sent to %s with subject '%s'", target_recipient, subject)

    return result
