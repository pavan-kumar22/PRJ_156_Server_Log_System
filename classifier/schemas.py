"""Pydantic schemas for the log classification API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request containing a complete server log event."""

    timestamp: str | None = None
    uuid: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    client_ip: str | None = None
    response_time_ms: int | float | None = None
    latency: int | float | None = None
    status_code: int | None = None
    endpoint: str | None = None
    method: str | None = None
    service: str | None = None
    host: str | None = None
    container: str | None = None
    region: str | None = None
    level: str | None = None

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Log message to classify.",
    )

    payload: dict[str, Any] | None = None


class ClassificationResponse(BaseModel):
    """Response returned after log classification."""

    timestamp: str | None = None
    uuid: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    client_ip: str | None = None
    response_time_ms: int | float | None = None
    latency: int | float | None = None
    status_code: int | None = None
    endpoint: str | None = None
    method: str | None = None
    service: str | None = None
    host: str | None = None
    container: str | None = None
    region: str | None = None
    level: str | None = None
    message: str
    payload: dict[str, Any] | None = None
    category: str
    confidence: float