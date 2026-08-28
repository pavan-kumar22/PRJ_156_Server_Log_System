"""FastAPI application for AI-based log classification."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, Request
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk

from classifier.model import LogClassifier
from classifier.schemas import (
    ClassificationRequest,
    ClassificationResponse,
)


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

    host_parts = host.split(":")

    return OpenSearch(
        hosts=[
            {
                "host": host_parts[0],
                "port": int(host_parts[1]) if len(host_parts) > 1 else 9200,
            }
        ],
        use_ssl=OPENSEARCH_HOST.startswith("https://"),
        verify_certs=False,
        ssl_show_warn=False,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )


opensearch_client = create_opensearch_client()


ALERT_CATEGORIES = {
    "Security Threat",
    "System Failure",
    "Performance Degradation",
}

ALERT_LEVELS = {
    "CRITICAL",
    "ERROR",
}


def should_notify(
    request: ClassificationRequest,
    category: str,
) -> bool:
    """Determine whether a classified event requires notification."""

    if category in ALERT_CATEGORIES:
        return True

    if request.level and request.level.upper() in ALERT_LEVELS:
        return True

    if (
        request.status_code is not None
        and request.status_code >= 500
    ):
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


def classify_event(
    request: ClassificationRequest,
) -> tuple[ClassificationRequest, str, float]:
    """Classify one event."""

    category, confidence = classifier.predict(
        request.message
    )

    return request, category, confidence


def save_classified_logs(
    classified_events: list[
        tuple[ClassificationRequest, str, float]
    ],
) -> list[dict[str, Any]]:
    """Bulk-save classified events into OpenSearch."""

    if not classified_events:
        return []

    index_name = get_classified_index()

    actions = []

    documents = []

    for request, category, confidence in classified_events:
        document = request.model_dump()

        document["category"] = category
        document["confidence"] = confidence

        documents.append(document)

        actions.append(
            {
                "_index": index_name,
                "_source": document,
            }
        )

    success_count, failed_items = bulk(
        opensearch_client,
        actions,
        chunk_size=50,
        request_timeout=30,
        raise_on_error=False,
    )

    if failed_items:
        LOGGER.error(
            "OpenSearch bulk indexing completed with failures: "
            "success=%s failed=%s",
            success_count,
            len(failed_items),
        )

        raise RuntimeError(
            f"OpenSearch bulk indexing failed for "
            f"{len(failed_items)} events."
        )

    LOGGER.info(
        "Classified logs stored in OpenSearch: "
        "index=%s events=%s",
        index_name,
        success_count,
    )

    return documents


@app.api_route("/health", methods=["GET", "POST"])
def health() -> dict[str, str]:
    """Return the health status of the classification service."""

    return {
        "status": "healthy",
        "service": "log-classifier",
        "model": "TF-IDF + LinearSVC",
    }


@app.post("/debug-vector")
async def debug_vector(
    request: Request,
) -> dict[str, Any]:
    """Return the raw JSON received from Vector."""

    body = await request.json()

    LOGGER.info(
        "RAW VECTOR REQUEST: %s",
        body,
    )

    return {
        "received": True,
        "body": body,
    }


@app.post("/classify")
def classify(
    request: ClassificationRequest | list[ClassificationRequest],
) -> ClassificationResponse | list[ClassificationResponse]:
    """
    Classify one or more server log events.

    Vector normally sends a JSON array when batching is enabled.
    Direct API testing can still send a single JSON object.
    """

    try:
        # Normalize input into a list.
        if isinstance(request, list):
            if not request:
                raise HTTPException(
                    status_code=422,
                    detail="Empty log event received.",
                )

            requests_to_classify = request

        else:
            requests_to_classify = [request]

        LOGGER.info(
            "Classification request received: events=%s",
            len(requests_to_classify),
        )

        # ---------------------------------------------------------
        # Phase 1: ML classification
        # ---------------------------------------------------------

        classified_events = []

        for log_request in requests_to_classify:
            event = classify_event(log_request)
            classified_events.append(event)

        # ---------------------------------------------------------
        # Phase 2: Bulk OpenSearch persistence
        # ---------------------------------------------------------

        save_classified_logs(
            classified_events
        )

        # ---------------------------------------------------------
        # Phase 3: Notifications
        #
        # Kept compatible with the existing notification system.
        # ---------------------------------------------------------

        for (
            log_request,
            category,
            confidence,
        ) in classified_events:

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

        # ---------------------------------------------------------
        # Build response
        # ---------------------------------------------------------

        responses = [
            ClassificationResponse(
                **log_request.model_dump(),
                category=category,
                confidence=confidence,
            )
            for (
                log_request,
                category,
                confidence,
            ) in classified_events
        ]

        if isinstance(request, list):
            return responses

        return responses[0]

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