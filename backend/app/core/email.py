import email.mime.multipart
import email.mime.text
import logging
import smtplib

import httpx

from app.core.config import settings

logger = logging.getLogger("krishilink.email")


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
) -> bool:
    """
    Send transactional email using configured provider:
    1. Resend REST API (if RESEND_API_KEY is configured)
    2. SMTP (if SMTP_HOST is configured)
    3. Mock logging fallback for development / test environments
    """
    # 1. Resend Provider
    if settings.resend_api_key:
        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "from": settings.email_from,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content or html_content,
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code in (200, 201):
                    logger.info("Email sent via Resend to %s: %s", to_email, subject)
                    return True
                logger.error("Resend API error (%s): %s", res.status_code, res.text)
                return False
        except Exception as exc:
            logger.error("Failed sending email via Resend: %s", exc)
            return False

    # 2. SMTP Provider
    if settings.smtp_host:
        try:
            msg = email.mime.multipart.MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.email_from
            msg["To"] = to_email

            if text_content:
                msg.attach(email.mime.text.MIMEText(text_content, "plain"))
            msg.attach(email.mime.text.MIMEText(html_content, "html"))

            if settings.smtp_port == 465:
                smtp_server: smtplib.SMTP = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10)
            else:
                smtp_server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
                smtp_server.starttls()

            if settings.smtp_user and settings.smtp_password:
                smtp_server.login(settings.smtp_user, settings.smtp_password)

            smtp_server.sendmail(settings.email_from, [to_email], msg.as_string())
            smtp_server.quit()
            logger.info("Email sent via SMTP to %s: %s", to_email, subject)
            return True
        except Exception as exc:
            logger.error("Failed sending email via SMTP: %s", exc)
            return False

    # 3. Development / Mock fallback
    logger.info(
        "[EMAIL DEV MOCK] To: %s | Subject: %s | (Configure RESEND_API_KEY or SMTP_HOST in production)",
        to_email,
        subject,
    )
    return True
