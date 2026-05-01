"""Email report support for processed news summaries."""

import smtplib
from email.message import EmailMessage
from typing import Dict, List

from analytics import analyze_results, format_analytics
from config import Config


def build_email_body(results: List[Dict]) -> str:
    """Build a plain-text email body from processed results."""
    lines = ["Daily News Summary", "=" * 80, ""]

    for index, result in enumerate(results, 1):
        lines.extend(
            [
                f"{index}. {result.get('title', 'Untitled')}",
                f"Source: {result.get('source', 'Unknown')}",
                f"Published: {result.get('published_at', '')}",
                f"URL: {result.get('url', '')}",
                f"Summary: {result.get('summary', '')}",
                f"Sentiment: {result.get('sentiment', '')}",
                "",
            ]
        )

    lines.extend(["Analytics", "-" * 80, format_analytics(analyze_results(results))])
    return "\n".join(lines)


def send_email_report(results: List[Dict], subject: str = "Daily News Summary"):
    """Send processed results as a plain-text email."""
    missing = [
        name
        for name, value in [
            ("EMAIL_HOST", Config.EMAIL_HOST),
            ("EMAIL_PORT", Config.EMAIL_PORT),
            ("EMAIL_USERNAME", Config.EMAIL_USERNAME),
            ("EMAIL_PASSWORD", Config.EMAIL_PASSWORD),
            ("EMAIL_FROM", Config.EMAIL_FROM),
            ("EMAIL_TO", Config.EMAIL_TO),
        ]
        if not value
    ]
    if missing:
        raise ValueError(f"Missing email configuration: {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = Config.EMAIL_FROM
    message["To"] = Config.EMAIL_TO
    message.set_content(build_email_body(results))

    with smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT, timeout=Config.REQUEST_TIMEOUT) as smtp:
        smtp.starttls()
        smtp.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        smtp.send_message(message)
