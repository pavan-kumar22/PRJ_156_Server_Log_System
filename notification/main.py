
"""Notification service for the AICTE server log observability platform."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

LOGGER = logging.getLogger("notification")


SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "").strip()


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
    """Receive and process an alert notification."""

    message = build_alert_message(event)

    LOGGER.warning("\n%s", message)

    slack_sent = send_slack_notification(event)

    return {
        "status": "accepted",
        "category": event.category,
        "severity": event.level,
        "slack_sent": slack_sent,
    }
