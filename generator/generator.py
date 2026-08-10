"""
Synthetic AICTE server log generator.

This module generates realistic structured JSON logs for simulated
e-governance services. The generated logs are written to a rotating
log file and will later be consumed by Vector.
"""

from __future__ import annotations

import json
import logging
import os
import random
import socket
import time
import uuid
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_FILE = LOG_DIR / "application.log"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOG_INTERVAL_SECONDS = float(
    os.getenv("LOG_INTERVAL_SECONDS", "1")
)

MAX_LOG_FILE_BYTES = int(
    os.getenv("MAX_LOG_FILE_BYTES", str(10 * 1024 * 1024))
)

BACKUP_COUNT = int(
    os.getenv("BACKUP_COUNT", "5")
)

REGION = os.getenv(
    "REGION",
    "ap-south-1"
)

HOST = os.getenv(
    "HOST_NAME",
    socket.gethostname()
)

CONTAINER = os.getenv(
    "CONTAINER_NAME",
    "aicte-log-generator"
)


SERVICES = [
    "student-portal",
    "payment-gateway",
    "faculty-verification-engine",
    "approval-workflow-service",
    "authentication-service",
    "document-service",
]


SERVICE_CONFIG: dict[str, dict[str, Any]] = {
    "student-portal": {
        "endpoints": [
            ("/api/v1/students/profile", "GET"),
            ("/api/v1/students/applications", "GET"),
            ("/api/v1/students/apply", "POST"),
            ("/api/v1/students/certificates", "GET"),
        ],
    },
    "payment-gateway": {
        "endpoints": [
            ("/api/v1/payments/initiate", "POST"),
            ("/api/v1/payments/status", "GET"),
            ("/api/v1/payments/refund", "POST"),
        ],
    },
    "faculty-verification-engine": {
        "endpoints": [
            ("/api/v1/faculty/verify", "POST"),
            ("/api/v1/faculty/applications", "GET"),
            ("/api/v1/faculty/review", "POST"),
        ],
    },
    "approval-workflow-service": {
        "endpoints": [
            ("/api/v1/approvals/submit", "POST"),
            ("/api/v1/approvals/status", "GET"),
            ("/api/v1/approvals/approve", "POST"),
            ("/api/v1/approvals/reject", "POST"),
        ],
    },
    "authentication-service": {
        "endpoints": [
            ("/api/v1/auth/login", "POST"),
            ("/api/v1/auth/logout", "POST"),
            ("/api/v1/auth/refresh", "POST"),
            ("/api/v1/auth/verify-token", "POST"),
        ],
    },
    "document-service": {
        "endpoints": [
            ("/api/v1/documents/upload", "POST"),
            ("/api/v1/documents/download", "GET"),
            ("/api/v1/documents/delete", "DELETE"),
            ("/api/v1/documents/verify", "POST"),
        ],
    },
}


class JsonFormatter(logging.Formatter):
    """Format Python log records as single-line JSON documents."""

    def format(self, record: logging.LogRecord) -> str:
        """Convert a logging record into a JSON document."""
        try:
            log_data = json.loads(record.getMessage())
        except json.JSONDecodeError:
            log_data = {
                "message": record.getMessage(),
            }

        return json.dumps(
            log_data,
            separators=(",", ":"),
            ensure_ascii=False,
        )


def create_logger() -> logging.Logger:
    """Create and configure the rotating application logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("aicte-log-generator")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_LOG_FILE_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger


def generate_uuid() -> str:
    """Generate a UUID for a log event."""
    return str(uuid.uuid4())


def generate_trace_id() -> str:
    """Generate a trace identifier."""
    return uuid.uuid4().hex


def generate_request_id() -> str:
    """Generate a request identifier."""
    return uuid.uuid4().hex


def generate_client_ip() -> str:
    """Generate a synthetic private client IP address."""
    return (
        f"10.{random.randint(0, 255)}."
        f"{random.randint(0, 255)}."
        f"{random.randint(1, 254)}"
    )


def generate_response_time() -> tuple[int, int]:
    """Generate latency and response time values."""
    latency = random.randint(20, 1200)
    response_time = latency + random.randint(0, 80)

    return response_time, latency


def generate_status_code(level: str) -> int:
    """Generate an HTTP status code appropriate for the log level."""
    if level == "INFO":
        return random.choice([200, 200, 200, 201, 204])

    if level == "WARNING":
        return random.choice([200, 400, 401, 404, 408, 429])

    if level == "ERROR":
        return random.choice([400, 401, 403, 404, 408, 422, 500, 502, 503])

    return random.choice([500, 502, 503, 504])


def generate_fake_payload(service: str) -> dict[str, Any]:
    """Generate synthetic request payload data.

    The payload intentionally contains fake PII-like values so that the
    PII masking stage can later be demonstrated.
    """
    payloads = {
        "student-portal": [
            {
                "student_id": f"STU{random.randint(100000, 999999)}",
                "email": "student@example.gov.in",
                "phone": "9876543210",
            },
            {
                "application_id": (
                    f"APP{random.randint(100000, 999999)}"
                ),
                "document_type": random.choice(
                    ["degree", "marksheet", "certificate"]
                ),
            },
        ],
        "payment-gateway": [
            {
                "transaction_id": (
                    f"TXN{random.randint(100000, 999999)}"
                ),
                "amount": random.choice([500, 1000, 2500, 5000]),
                "currency": "INR",
            },
            {
                "transaction_id": (
                    f"TXN{random.randint(100000, 999999)}"
                ),
                "payment_method": random.choice(
                    ["UPI", "CARD", "NETBANKING"]
                ),
            },
        ],
        "faculty-verification-engine": [
            {
                "faculty_id": f"FAC{random.randint(10000, 99999)}",
                "email": "faculty@example.gov.in",
            },
            {
                "application_id": (
                    f"APP{random.randint(100000, 999999)}"
                ),
                "verification_type": "academic",
            },
        ],
        "approval-workflow-service": [
            {
                "request_id": (
                    f"REQ{random.randint(100000, 999999)}"
                ),
                "approval_stage": random.choice(
                    ["faculty", "department", "admin"]
                ),
            },
            {
                "application_id": (
                    f"APP{random.randint(100000, 999999)}"
                ),
                "decision": random.choice(
                    ["approved", "rejected", "pending"]
                ),
            },
        ],
        "authentication-service": [
            {
                "username": random.choice(
                    ["student001", "faculty001", "admin001"]
                ),
                "email": "user@example.gov.in",
            },
            {
                "username": random.choice(
                    ["student001", "faculty001", "admin001"]
                ),
                "pan": "ABCDE1234F",
            },
        ],
        "document-service": [
            {
                "document_id": (
                    f"DOC{random.randint(100000, 999999)}"
                ),
                "document_type": random.choice(
                    ["certificate", "marksheet", "identity-proof"]
                ),
            },
            {
                "document_id": (
                    f"DOC{random.randint(100000, 999999)}"
                ),
                "email": "student@example.gov.in",
            },
        ],
    }

    return random.choice(payloads[service])


def generate_normal_event(
    service: str,
) -> tuple[str, str]:
    """Generate a normal application event."""
    events = {
        "student-portal": [
            (
                "INFO",
                "Student profile retrieved successfully",
            ),
            (
                "INFO",
                "Student application submitted successfully",
            ),
            (
                "INFO",
                "Certificate information retrieved",
            ),
        ],
        "payment-gateway": [
            (
                "INFO",
                "Payment transaction completed successfully",
            ),
            (
                "INFO",
                "Payment status retrieved successfully",
            ),
        ],
        "faculty-verification-engine": [
            (
                "INFO",
                "Faculty verification completed successfully",
            ),
            (
                "INFO",
                "Faculty application retrieved",
            ),
        ],
        "approval-workflow-service": [
            (
                "INFO",
                "Approval request submitted successfully",
            ),
            (
                "INFO",
                "Approval request status retrieved",
            ),
        ],
        "authentication-service": [
            (
                "INFO",
                "User authentication successful",
            ),
            (
                "INFO",
                "User session created successfully",
            ),
            (
                "INFO",
                "Authentication token refreshed",
            ),
        ],
        "document-service": [
            (
                "INFO",
                "Document uploaded successfully",
            ),
            (
                "INFO",
                "Document downloaded successfully",
            ),
            (
                "INFO",
                "Document verification completed",
            ),
        ],
    }

    return random.choice(events[service])


def generate_performance_event(
    service: str,
) -> tuple[str, str]:
    """Generate an application performance event."""
    events = {
        "student-portal": [
            (
                "WARNING",
                "Student profile request exceeded latency threshold",
            ),
            (
                "ERROR",
                "Student application request timed out",
            ),
        ],
        "payment-gateway": [
            (
                "WARNING",
                "Payment gateway response latency is increasing",
            ),
            (
                "ERROR",
                "Payment gateway request timed out",
            ),
        ],
        "faculty-verification-engine": [
            (
                "WARNING",
                "Faculty verification processing is slow",
            ),
            (
                "ERROR",
                "Faculty verification request timed out",
            ),
        ],
        "approval-workflow-service": [
            (
                "WARNING",
                "Approval workflow processing latency is high",
            ),
            (
                "ERROR",
                "Approval workflow request timed out",
            ),
        ],
        "authentication-service": [
            (
                "WARNING",
                "Authentication service response latency is high",
            ),
            (
                "ERROR",
                "Authentication request timed out",
            ),
        ],
        "document-service": [
            (
                "WARNING",
                "Document upload processing is slow",
            ),
            (
                "ERROR",
                "Document service request timed out",
            ),
        ],
    }

    return random.choice(events[service])


def generate_security_event(
    service: str,
) -> tuple[str, str]:
    """Generate a synthetic security-related event."""
    events = {
        "authentication-service": [
            (
                "WARNING",
                "Multiple failed authentication attempts detected",
            ),
            (
                "ERROR",
                "Invalid authentication token received",
            ),
            (
                "CRITICAL",
                "Possible brute force authentication activity detected",
            ),
            (
                "CRITICAL",
                "Unauthorized administrative access attempt detected",
            ),
        ],
        "student-portal": [
            (
                "WARNING",
                "Unauthorized access attempt detected",
            ),
            (
                "ERROR",
                "Access denied for protected student resource",
            ),
        ],
        "payment-gateway": [
            (
                "WARNING",
                "Suspicious payment request pattern detected",
            ),
            (
                "CRITICAL",
                "Potential fraudulent payment activity detected",
            ),
        ],
        "faculty-verification-engine": [
            (
                "WARNING",
                "Unauthorized faculty verification request detected",
            ),
        ],
        "approval-workflow-service": [
            (
                "WARNING",
                "Unauthorized approval workflow access detected",
            ),
        ],
        "document-service": [
            (
                "WARNING",
                "Unauthorized document access attempt detected",
            ),
            (
                "CRITICAL",
                "Suspicious repeated document access detected",
            ),
        ],
    }

    return random.choice(events[service])


def generate_system_failure_event(
    service: str,
) -> tuple[str, str]:
    """Generate a synthetic system failure event."""
    events = {
        "student-portal": [
            (
                "ERROR",
                "Student portal database connection failed",
            ),
            (
                "CRITICAL",
                "Student portal dependency is unavailable",
            ),
        ],
        "payment-gateway": [
            (
                "ERROR",
                "Payment database connection failed",
            ),
            (
                "CRITICAL",
                "Payment gateway dependency is unavailable",
            ),
        ],
        "faculty-verification-engine": [
            (
                "ERROR",
                "Faculty verification database connection failed",
            ),
            (
                "CRITICAL",
                "Faculty verification service is unavailable",
            ),
        ],
        "approval-workflow-service": [
            (
                "ERROR",
                "Approval workflow database connection failed",
            ),
            (
                "CRITICAL",
                "Approval workflow dependency is unavailable",
            ),
        ],
        "authentication-service": [
            (
                "ERROR",
                "Authentication database connection failed",
            ),
            (
                "CRITICAL",
                "Authentication service dependency is unavailable",
            ),
        ],
        "document-service": [
            (
                "ERROR",
                "Document storage connection failed",
            ),
            (
                "CRITICAL",
                "Document service dependency is unavailable",
            ),
        ],
    }

    return random.choice(events[service])


def select_event(
    service: str,
) -> tuple[str, str]:
    """Select an event category using weighted probabilities."""
    category = random.choices(
        population=[
            "routine",
            "performance",
            "security",
            "failure",
        ],
        weights=[
            75,
            12,
            8,
            5,
        ],
        k=1,
    )[0]

    if category == "routine":
        return generate_normal_event(service)

    if category == "performance":
        return generate_performance_event(service)

    if category == "security":
        return generate_security_event(service)

    return generate_system_failure_event(service)


def build_log_record() -> dict[str, Any]:
    """Build one complete structured log record."""
    service = random.choice(SERVICES)

    endpoint, method = random.choice(
        SERVICE_CONFIG[service]["endpoints"]
    )

    level, message = select_event(service)

    response_time_ms, latency = generate_response_time()

    status_code = generate_status_code(level)

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat().replace("+00:00", "Z"),
        "uuid": generate_uuid(),
        "trace_id": generate_trace_id(),
        "request_id": generate_request_id(),
        "client_ip": generate_client_ip(),
        "response_time_ms": response_time_ms,
        "latency": latency,
        "status_code": status_code,
        "endpoint": endpoint,
        "method": method,
        "service": service,
        "host": HOST,
        "container": CONTAINER,
        "region": REGION,
        "level": level,
        "message": message,
        "payload": generate_fake_payload(service),
    }


def run_generator(logger: logging.Logger) -> None:
    """Continuously generate and write structured logs."""
    logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat().replace("+00:00", "Z"),
                "uuid": generate_uuid(),
                "trace_id": generate_trace_id(),
                "request_id": generate_request_id(),
                "client_ip": "10.0.0.1",
                "response_time_ms": 0,
                "latency": 0,
                "status_code": 200,
                "endpoint": "/generator/start",
                "method": "SYSTEM",
                "service": "log-generator",
                "host": HOST,
                "container": CONTAINER,
                "region": REGION,
                "level": "INFO",
                "message": "AICTE synthetic log generator started",
                "payload": {
                    "services": SERVICES,
                },
            }
        )
    )

    print(f"Log generator started.")
    print(f"Log file: {LOG_FILE}")
    print(f"Interval: {LOG_INTERVAL_SECONDS} seconds")
    print("Press CTRL+C to stop.")

    try:
        while True:
            record = build_log_record()

            logger.log(
                getattr(
                    logging,
                    record["level"],
                    logging.INFO,
                ),
                json.dumps(record),
            )

            print(
                f"[{record['level']}] "
                f"{record['service']} - "
                f"{record['message']}"
            )

            time.sleep(LOG_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat().replace("+00:00", "Z"),
                    "uuid": generate_uuid(),
                    "trace_id": generate_trace_id(),
                    "request_id": generate_request_id(),
                    "client_ip": "10.0.0.1",
                    "response_time_ms": 0,
                    "latency": 0,
                    "status_code": 200,
                    "endpoint": "/generator/stop",
                    "method": "SYSTEM",
                    "service": "log-generator",
                    "host": HOST,
                    "container": CONTAINER,
                    "region": REGION,
                    "level": "INFO",
                    "message": "AICTE synthetic log generator stopped",
                    "payload": {},
                }
            )
        )

        print("\nLog generator stopped.")


def main() -> None:
    """Configure logging and start the generator."""
    logger = create_logger()
    run_generator(logger)


if __name__ == "__main__":
    main()