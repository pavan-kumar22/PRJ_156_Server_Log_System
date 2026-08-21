"""Notification service for the AICTE server log observability platform."""

from __future__ import annotations

import hashlib
import logging
import os
import smtplib
import time
from email.message import EmailMessage
from typing import Any

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from notification.sanitizer import sanitize_text

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

LOGGER = logging.getLogger("notification")


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "").strip()

SMTP_SERVER = os.getenv("SMTP_SERVER", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "").strip()

SECURITY_ALERT_CONFIDENCE_THRESHOLD = 0.60

# Deduplication window
ALERT_DEDUP_WINDOW_SECONDS = int(
    os.getenv("ALERT_DEDUP_WINDOW_SECONDS", "300")
)

# In-memory storage of recently processed alert fingerprints
_recent_alerts: dict[str, float] = {}


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AICTE Notification Service",
    description="Notification service for classified server log alerts.",
    version="1.0.0",
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class NotificationRequest(BaseModel):
    category: str
    confidence: float
    level: str | None = None
    service: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    message: str
    timestamp: str | None = None


# ============================================================
# ALERT RULES
# ============================================================

def should_alert(event: NotificationRequest) -> tuple[bool, str]:
    """Determine whether an event should generate an alert."""

    level = (event.level or "").upper().strip()
    category = event.category.strip()

    # Rule 1: CRITICAL events always generate alerts.
    if level == "CRITICAL":
        return True, "critical severity"

    # Rule 2: Security threats above confidence threshold.
    if (
        category == "Security Threat"
        and event.confidence >= SECURITY_ALERT_CONFIDENCE_THRESHOLD
    ):
        return True, "security threat above confidence threshold"
    # Rule 3: Performance degradation generates alerts.
    if category == "Performance Degradation":
        return True, "performance degradation detected"
    
    # Rule 4: HTTP 5xx responses generate alerts.
    if event.status_code is not None and event.status_code >= 500:
        return True, "HTTP 5xx server error"

    # Rule 5: ERROR-level events generate alerts.
    if level == "ERROR":
        return True, "error severity"

    # INFO and WARNING events normally do not generate alerts.
    return False, "below alert threshold"


# ============================================================
# ALERT MESSAGE
# ============================================================

def build_alert_message(event: NotificationRequest) -> str:
    """Build a human-readable sanitized alert message."""

    sanitized_message = sanitize_text(event.message)
    sanitized_service = sanitize_text(event.service or "UNKNOWN")
    sanitized_endpoint = sanitize_text(event.endpoint or "UNKNOWN")

    return (
        "🚨 AICTE SERVER LOG ALERT\n"
        f"Category: {event.category}\n"
        f"Confidence: {event.confidence:.3f}\n"
        f"Severity: {event.level or 'UNKNOWN'}\n"
        f"Service: {sanitized_service}\n"
        f"Endpoint: {sanitized_endpoint}\n"
        f"Status Code: {event.status_code or 'UNKNOWN'}\n"
        f"Timestamp: {event.timestamp or 'UNKNOWN'}\n"
        f"Message: {sanitized_message}"
    )


# ============================================================
# ALERT FINGERPRINT
# ============================================================

def create_alert_fingerprint(event: NotificationRequest) -> str:
    """
    Create a stable fingerprint for alert deduplication.

    Timestamp is intentionally excluded so that the same alert
    occurring repeatedly within the deduplication window is
    treated as a duplicate.
    """

    raw = "|".join(
        [
            event.category,
            event.service or "",
            event.endpoint or "",
            str(event.status_code or ""),
            event.message,
        ]
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# DEDUPLICATION
# ============================================================

def cleanup_old_alerts() -> None:
    """Remove expired alert fingerprints."""

    now = time.time()

    expired = [
        fingerprint
        for fingerprint, timestamp in _recent_alerts.items()
        if now - timestamp >= ALERT_DEDUP_WINDOW_SECONDS
    ]

    for fingerprint in expired:
        del _recent_alerts[fingerprint]


def is_duplicate_alert(event: NotificationRequest) -> bool:
    """Return True when the same alert was recently processed."""

    fingerprint = create_alert_fingerprint(event)
    now = time.time()

    previous_time = _recent_alerts.get(fingerprint)

    if previous_time is not None:
        if now - previous_time < ALERT_DEDUP_WINDOW_SECONDS:
            return True

    # Record this alert as recently processed.
    _recent_alerts[fingerprint] = now

    return False


# ============================================================
# SLACK NOTIFICATION
# ============================================================

def send_slack_notification(event: NotificationRequest) -> bool:
    """Send structured notification data to Slack."""

    if not SLACK_WEBHOOK_URL:
        LOGGER.info(
            "SLACK_WEBHOOK_URL is not configured. "
            "Slack notification skipped."
        )
        return False

    payload = {
        "category": event.category,
        "confidence": event.confidence,
        "level": event.level or "UNKNOWN",
        "service": sanitize_text(event.service or "UNKNOWN"),
        "endpoint": sanitize_text(event.endpoint or "UNKNOWN"),
        "status_code": event.status_code,
        "message": sanitize_text(event.message),
        "timestamp": event.timestamp or "UNKNOWN",
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        LOGGER.info("Slack notification sent successfully.")
        return True

    except requests.RequestException:
        LOGGER.exception("Failed to send Slack notification.")
        return False


# ============================================================
# EMAIL NOTIFICATION
# ============================================================

def send_email_notification(event: NotificationRequest) -> bool:
    """Send an email notification when SMTP is configured."""

    if not all(
        [
            SMTP_SERVER,
            SMTP_PORT,
            SMTP_USERNAME,
            SMTP_PASSWORD,
            ALERT_EMAIL_TO,
        ]
    ):
        LOGGER.info(
            "SMTP configuration is incomplete. "
            "Email notification skipped."
        )
        return False

    subject = (
        f"[AICTE ALERT] {event.level or 'UNKNOWN'} - "
        f"{event.category}"
    )

    body = build_alert_message(event)

    email_message = EmailMessage()
    email_message["From"] = SMTP_USERNAME
    email_message["To"] = ALERT_EMAIL_TO
    email_message["Subject"] = subject
    email_message.set_content(body)

    try:
        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=10,
        ) as server:

            server.starttls()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.send_message(email_message)

        LOGGER.info("Email notification sent successfully.")
        return True

    except Exception:
        LOGGER.exception("Failed to send email notification.")
        return False


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint."""

    return {
        "status": "healthy",
        "service": "notification-service",
    }


# ============================================================
# NOTIFICATION ENDPOINT
# ============================================================

@app.post("/notify")
def notify(event: NotificationRequest) -> dict[str, Any]:
    """Receive an event and apply alert routing rules."""

    # --------------------------------------------------------
    # STEP 1: Determine whether event requires an alert
    # --------------------------------------------------------

    should_send_alert, reason = should_alert(event)

    # --------------------------------------------------------
    # STEP 2: Ignore normal events
    # --------------------------------------------------------

    if not should_send_alert:

        LOGGER.info(
            "Event did not meet alert threshold: "
            "category=%s level=%s confidence=%.3f "
            "status_code=%s reason=%s",
            event.category,
            event.level,
            event.confidence,
            event.status_code,
            reason,
        )

        return {
            "status": "accepted",
            "alert": False,
            "reason": reason,
            "category": event.category,
            "severity": event.level,
            "slack_sent": False,
            "email_sent": False,
        }

    # --------------------------------------------------------
    # STEP 3: Cleanup expired fingerprints
    # --------------------------------------------------------

    cleanup_old_alerts()

    # --------------------------------------------------------
    # STEP 4: Check duplicate BEFORE sending notifications
    # --------------------------------------------------------

    if is_duplicate_alert(event):

        LOGGER.info(
            "Duplicate alert suppressed: "
            "category=%s service=%s endpoint=%s message=%s",
            event.category,
            event.service,
            event.endpoint,
            event.message,
        )

        return {
            "status": "suppressed",
            "alert": False,
            "reason": "duplicate alert",
            "category": event.category,
            "severity": event.level,
            "slack_sent": False,
            "email_sent": False,
        }

    # --------------------------------------------------------
    # STEP 5: Build and log alert
    # --------------------------------------------------------

    message = build_alert_message(event)

    LOGGER.warning(
        "\n%s\nAlert rule matched: %s",
        message,
        reason,
    )

    # --------------------------------------------------------
    # STEP 6: Send notifications
    # --------------------------------------------------------

    slack_sent = send_slack_notification(event)

    email_sent = send_email_notification(event)

    # --------------------------------------------------------
    # STEP 7: Return result
    # --------------------------------------------------------

    return {
        "status": "accepted",
        "alert": True,
        "reason": reason,
        "category": event.category,
        "severity": event.level,
        "slack_sent": slack_sent,
        "email_sent": email_sent,
    }