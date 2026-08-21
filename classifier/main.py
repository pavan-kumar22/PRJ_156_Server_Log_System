"""FastAPI application for AI-based log classification."""

from __future__ import annotations

import logging
import os
from typing import Any
import requests
from fastapi import FastAPI, HTTPException
from opensearchpy import OpenSearch

from classifier.model import LogClassifier
from classifier.schemas import (
    ClassificationRequest,
    ClassificationResponse,
)
from fastapi import FastAPI, HTTPException, Request

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

LOGGER = logging.getLogger(__name__)


OPENSEARCH_HOST = os.getenv(
    "OPENSEARCH_HOST",
    "http://opensearch:9200",
)
NOTIFICATION_URL = os.getenv(
    "NOTIFICATION_URL",
    "http://notification:8001/notify",
)

from datetime import datetime, timezone


def get_classified_index() -> str:
    """Return the classified-log index for the current UTC date."""
    current_date = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    return f"aicte-classified-{current_date}"


app = FastAPI(
    title="AICTE Log Classification Service",
    description=(
        "AI-based content classification service for "
        "the AICTE server log observability platform."
    ),
    version="1.0.0",
)


classifier = LogClassifier()


def create_opensearch_client() -> OpenSearch:
    """Create an OpenSearch client from environment configuration."""
    host = OPENSEARCH_HOST.replace("http://", "").replace(
        "https://",
        "",
    )

    return OpenSearch(
        hosts=[
            {
                "host": host.split(":")[0],
                "port": int(host.split(":")[1]),
            }
        ],
        use_ssl=OPENSEARCH_HOST.startswith("https://"),
        verify_certs=False,
        ssl_show_warn=False,
    )


opensearch_client = create_opensearch_client()


def save_classified_log(
    request: ClassificationRequest,
    category: str,
    confidence: float,
) -> dict[str, Any]:
    """Save the classified log event into OpenSearch."""
    document = request.model_dump()

    document["category"] = category
    document["confidence"] = confidence

    response = opensearch_client.index(
        index=get_classified_index(),
        body=document,
    )

    LOGGER.info(
        "Classified log stored in OpenSearch: "
        "index=%s id=%s category=%s",
        get_classified_index(),
        response.get("_id"),
        category,
    )

    return document

ALERT_CATEGORIES = {
    "Security Threat",
    "System Failure",
    "Performance Degradation",
}

ALERT_LEVELS = {
    "CRITICAL",
    "ERROR",
}


def should_notify(request: ClassificationRequest, category: str) -> bool:
    """Determine whether a classified event requires notification."""

    # Security, system failures and performance degradation
    # should be sent to the notification service.
    if category in ALERT_CATEGORIES:
        return True

    # ERROR and CRITICAL events should generate alerts.
    if request.level and request.level.upper() in ALERT_LEVELS:
        return True

    # Any HTTP 5xx server error should generate an alert.
    if request.status_code is not None and request.status_code >= 500:
        return True

    return False


def send_notification(
    request: ClassificationRequest,
    category: str,
    confidence: float,
) -> None:
    """Send an alert to the notification service."""

    if not should_notify(request, category):
        return

    payload = {
        "category": category,
        "confidence": confidence,
        "level": request.level,
        "service": request.service,
        "endpoint": request.endpoint,
        "status_code": request.status_code,
        "message": request.message,
        "timestamp": request.timestamp,
    }

    try:
        response = requests.post(
            NOTIFICATION_URL,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        LOGGER.warning(
            "Notification sent: category=%s service=%s",
            category,
            request.service,
        )

    except requests.RequestException:
        LOGGER.exception(
            "Failed to send notification for category=%s",
            category,
        )

@app.api_route("/health", methods=["GET", "POST"])
def health() -> dict[str, str]:
    """Return the health status of the classification service."""
    return {
        "status": "healthy",
        "service": "log-classifier",
        "model": "TF-IDF + LinearSVC",
    }
@app.post("/debug-vector")
async def debug_vector(request: Request) -> dict[str, Any]:
    """Return the raw JSON received from Vector for debugging."""
    body = await request.json()

    LOGGER.info(
        "RAW VECTOR REQUEST: %s",
        body,
    )

    return {
        "received": True,
        "body": body,
    }

@app.post(
    "/classify",
    response_model=ClassificationResponse,
)
def classify(
    request: ClassificationRequest | list[ClassificationRequest],
) -> ClassificationResponse:
    """Classify a server log and store the result."""

    try:
        # Vector sends one log event as a JSON array.
        # Direct API testing can still send a single JSON object.
        if isinstance(request, list):
            if not request:
                raise HTTPException(
                    status_code=422,
                    detail="Empty log event received.",
                )

            log_request = request[0]
        else:
            log_request = request

        category, confidence = classifier.predict(
            log_request.message
        )

        save_classified_log(
            request=log_request,
            category=category,
            confidence=confidence,
        )

        send_notification(
            request=log_request,
            category=category,
            confidence=confidence,
        )

        LOGGER.info(
            "Log classified successfully: "
            "service=%s category=%s confidence=%.4f",
            log_request.service,
            category,
            confidence,
        )

        return ClassificationResponse(
            **log_request.model_dump(),
            category=category,
            confidence=confidence,
        )

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Log classification or OpenSearch storage failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Log classification failed.",
        ) from exc