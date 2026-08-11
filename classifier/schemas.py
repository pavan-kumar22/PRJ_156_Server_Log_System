"""Pydantic schemas for the log classification API."""

from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request body containing the log message to classify."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Log message to classify.",
    )


class ClassificationResponse(BaseModel):
    """Response returned by the classification service."""

    message: str
    category: str
    confidence: float