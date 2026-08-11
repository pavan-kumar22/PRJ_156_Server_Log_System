"""FastAPI application for AI-based log classification."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

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

app = FastAPI(
    title="AICTE Log Classification Service",
    description=(
        "AI-based content classification service for "
        "the AICTE server log observability platform."
    ),
    version="1.0.0",
)

classifier = LogClassifier()


@app.get("/health")
def health() -> dict[str, str]:
    """Return the health status of the classification service."""
    return {
        "status": "healthy",
        "service": "log-classifier",
        "model": "TF-IDF + LinearSVC",
    }


@app.post(
    "/classify",
    response_model=ClassificationResponse,
)
def classify(
    request: ClassificationRequest,
) -> ClassificationResponse:
    """
    Classify a log message.

    Args:
        request: Request containing the log message.

    Returns:
        Classification response.

    Raises:
        HTTPException: If classification fails.
    """
    try:
        category, confidence = classifier.predict(
            request.message
        )

        LOGGER.info(
            "Log classified successfully: category=%s confidence=%.4f",
            category,
            confidence,
        )

        return ClassificationResponse(
            message=request.message,
            category=category,
            confidence=confidence,
        )

    except Exception as exc:
        LOGGER.exception("Log classification failed.")

        raise HTTPException(
            status_code=500,
            detail="Log classification failed.",
        ) from exc