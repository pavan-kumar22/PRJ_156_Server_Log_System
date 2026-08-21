"""
AICTE Demo Portal Action API.

Receives actions from the demo website and writes realistic
structured AICTE server logs into application.log.
"""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="AICTE Demo Action API",
    description="Bridge between the AICTE demo portal and the log monitoring platform.",
    version="1.0.0",
)


LOG_FILE = Path("/var/log/aicte/application.log")


class ActionRequest(BaseModel):
    action: str
    data: dict[str, Any] | None = None


def base_log(
    service: str,
    endpoint: str,
    method: str,
    level: str,
    status_code: int,
    message: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:

    latency = random.randint(80, 400)

    if level in {"WARNING", "ERROR", "CRITICAL"}:
        latency = random.randint(300, 1200)

    return {
        "timestamp": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),

        "uuid": str(uuid.uuid4()),
        "trace_id": uuid.uuid4().hex,
        "request_id": uuid.uuid4().hex,

        "client_ip": f"10.{random.randint(1, 254)}."
                      f"{random.randint(1, 254)}."
                      f"{random.randint(1, 254)}",

        "response_time_ms": latency,
        "latency": latency,

        "status_code": status_code,
        "endpoint": endpoint,
        "method": method,

        "service": service,
        "host": "aicte-demo-portal",
        "container": "aicte-demo-portal",
        "region": "ap-south-1",

        "level": level,
        "message": message,

        "payload": payload or {},
    }


ACTION_MAP = {

    # ---------------------------------------------------------
    # NORMAL APPLICATION EVENTS
    # ---------------------------------------------------------

    "login_success": lambda: base_log(
        "authentication-service",
        "/api/v1/auth/login",
        "POST",
        "INFO",
        200,
        "User authentication successful",
        {
            "username": "student001",
        },
    ),

    "profile_update": lambda: base_log(
        "student-portal",
        "/api/v1/students/profile",
        "PUT",
        "INFO",
        200,
        "Student profile updated successfully",
        {
            "student_id": "STU100001",
        },
    ),

    "document_upload": lambda: base_log(
        "document-service",
        "/api/v1/documents/upload",
        "POST",
        "INFO",
        201,
        "Document uploaded successfully",
        {
            "document_id": "DOC100001",
            "document_type": "certificate",
        },
    ),

    "payment_success": lambda: base_log(
        "payment-gateway",
        "/api/v1/payments/initiate",
        "POST",
        "INFO",
        200,
        "Payment transaction completed successfully",
        {
            "transaction_id": "TXN100001",
            "amount": 500,
            "currency": "INR",
        },
    ),

    # ---------------------------------------------------------
    # PERFORMANCE EVENTS
    # ---------------------------------------------------------

    "payment_timeout": lambda: base_log(
        "payment-gateway",
        "/api/v1/payments/initiate",
        "POST",
        "ERROR",
        504,
        "Payment gateway request timed out",
        {
            "transaction_id": "TXN100002",
        },
    ),

    "slow_response": lambda: base_log(
        "student-portal",
        "/api/v1/students/profile",
        "GET",
        "WARNING",
        200,
        "Student profile request exceeded latency threshold",
        {
            "response_time_ms": 1450,
        },
    ),

    # ---------------------------------------------------------
    # SECURITY EVENTS
    # ---------------------------------------------------------

    "unauthorized_login": lambda: base_log(
        "authentication-service",
        "/api/v1/auth/login",
        "POST",
        "CRITICAL",
        403,
        "Possible brute force authentication activity detected",
        {
            "attempts": 10,
        },
    ),

    "unauthorized_document": lambda: base_log(
        "document-service",
        "/api/v1/documents/download",
        "GET",
        "WARNING",
        401,
        "Unauthorized document access attempt detected",
        {
            "document_id": "DOC100002",
        },
    ),

    "fraudulent_payment": lambda: base_log(
        "payment-gateway",
        "/api/v1/payments/initiate",
        "POST",
        "CRITICAL",
        503,
        "Potential fraudulent payment activity detected",
        {
            "transaction_id": "TXN100003",
        },
    ),

    # ---------------------------------------------------------
    # SYSTEM FAILURE EVENTS
    # ---------------------------------------------------------

    "database_failure": lambda: base_log(
        "payment-gateway",
        "/api/v1/payments/initiate",
        "POST",
        "ERROR",
        503,
        "Payment database connection failed",
        {},
    ),

    "service_failure": lambda: base_log(
        "document-service",
        "/api/v1/documents/upload",
        "POST",
        "CRITICAL",
        500,
        "Document service dependency is unavailable",
        {},
    ),
}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "aicte-action-api",
    }


@app.get("/actions")
def available_actions() -> dict[str, list[str]]:
    return {
        "actions": list(ACTION_MAP.keys())
    }


@app.post("/api/action")
def execute_action(request: ActionRequest) -> dict[str, Any]:

    action = request.action.strip().lower()

    if action not in ACTION_MAP:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unknown action",
                "available_actions": list(ACTION_MAP.keys()),
            },
        )

    log_event = ACTION_MAP[action]()

    if request.data:
        log_event["payload"].update(request.data)

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                log_event,
                ensure_ascii=False,
            )
            + "\n"
        )

    return {
        "status": "accepted",
        "action": action,
        "message": "Demo action generated successfully",
        "event": log_event,
    }