"""Notification service for the AICTE server log observability platform."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from fastapi import FastAPI
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

LOGGER = logging.getLogger("notification")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "").strip()

SECURITY_ALERT_CONFIDENCE_THRESHOLD = 0.60


app = FastAPI(
    title="AICTE Notification Service",
    description="Notification service for classified server log alerts.",
    version="1.0.0",
)


class NotificationRequest(BaseModel):
    category: str
    confidence: float
    level: str | None = None
    service: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    message: str
    timestamp: str | None = None


def should_alert(event: NotificationRequest) -> tuple[bool, str]:
    """Determine whether an event should generate an alert."""

    level = (event.level or "").upper().strip()
    category = event.category.strip()

    # Rule 1: CRITICAL events always generate alerts.
    if level == "CRITICAL":
        return True, "critical severity"

    # Rule 2: Security threats above the confidence threshold generate alerts.
    if (
        category == "Security Threat"
        and event.confidence >= SECURITY_ALERT_CONFIDENCE_THRESHOLD
    ):
        return True, "security threat above confidence threshold"

    # Rule 3: HTTP 5xx responses generate alerts.
    if event.status_code is not None and event.status_code >= 500:
        return True, "HTTP 5xx server error"

    # Rule 4: ERROR-level events generate alerts.
    if level == "ERROR":
        return True, "error severity"

    # INFO and WARNING do not generate Slack alerts.
    return False, "below alert threshold"


def build_alert_message(event: NotificationRequest) -> str:
    """Build a human-readable alert message."""

    return (
        "🚨 AICTE SERVER LOG ALERT\n"
        f"Category: {event.category}\n"
        f"Confidence: {event.confidence:.3f}\n"
        f"Severity: {event.level or 'UNKNOWN'}\n"
        f"Service: {event.service or 'UNKNOWN'}\n"
        f"Endpoint: {event.endpoint or 'UNKNOWN'}\n"
        f"Status Code: {event.status_code or 'UNKNOWN'}\n"
        f"Timestamp: {event.timestamp or 'UNKNOWN'}\n"
        f"Message: {event.message}"
    )


def send_slack_notification(event: NotificationRequest) -> bool:
    """Send structured notification data to the Slack workflow webhook."""

    if not SLACK_WEBHOOK_URL:
        LOGGER.info(
            "SLACK_WEBHOOK_URL is not configured. "
            "Alert will remain in service logs."
        )
        return False

    payload = {
        "category": event.category,
        "confidence": event.confidence,
        "level": event.level or "UNKNOWN",
        "service": event.service or "UNKNOWN",
        "endpoint": event.endpoint or "UNKNOWN",
        "status_code": event.status_code,
        "message": event.message,
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


@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint."""

    return {
        "status": "healthy",
        "service": "notification-service",
    }


@app.post("/notify")
def notify(event: NotificationRequest) -> dict[str, Any]:
    """Receive an event and apply alert routing rules."""

    should_send_alert, reason = should_alert(event)

    message = build_alert_message(event)

    if should_send_alert:
        LOGGER.warning(
            "\n%s\nAlert rule matched: %s",
            message,
            reason,
        )

        slack_sent = send_slack_notification(event)

    else:
        LOGGER.info(
            "Event did not meet alert threshold: "
            "category=%s level=%s confidence=%.3f status_code=%s reason=%s",
            event.category,
            event.level,
            event.confidence,
            event.status_code,
            reason,
        )

        slack_sent = False

    return {
        "status": "accepted",
        "alert": should_send_alert,
        "reason": reason,
        "category": event.category,
        "severity": event.level,
        "slack_sent": slack_sent,
    }