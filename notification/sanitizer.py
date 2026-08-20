"""Sensitive data sanitization for AICTE alert notifications."""

from __future__ import annotations

import re


def mask_email(value: str) -> str:
    """Mask an email address while preserving its domain."""

    def replace(match: re.Match[str]) -> str:
        username = match.group(1)
        domain = match.group(2)

        if len(username) <= 2:
            masked_username = "*" * len(username)
        else:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]

        return f"{masked_username}@{domain}"

    return re.sub(
        r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
        replace,
        value,
    )


def mask_phone(value: str) -> str:
    """Mask phone numbers while preserving the last four digits."""

    def replace(match: re.Match[str]) -> str:
        number = match.group(0)

        digits = re.sub(r"\D", "", number)

        if len(digits) < 7:
            return number

        masked = "*" * (len(digits) - 4) + digits[-4:]

        return masked

    return re.sub(
        r"(?<!\d)(?:\+?\d[\d\s\-]{8,}\d)(?!\d)",
        replace,
        value,
    )


def mask_pan(value: str) -> str:
    """Mask PAN-like identifiers."""

    return re.sub(
        r"\b[A-Z]{5}\d{4}[A-Z]\b",
        lambda match: "XXXXX" + match.group(0)[5:],
        value,
    )


def mask_student_id(value: str) -> str:
    """Mask student identifiers while preserving the prefix and last digits."""

    def replace(match: re.Match[str]) -> str:
        identifier = match.group(0)

        if len(identifier) <= 6:
            return identifier

        return identifier[:3] + "*" * (len(identifier) - 5) + identifier[-2:]

    return re.sub(
        r"\bSTU\d{4,}\b",
        replace,
        value,
        flags=re.IGNORECASE,
    )


def mask_ip_address(value: str) -> str:
    """Partially mask IPv4 addresses."""

    def replace(match: re.Match[str]) -> str:
        parts = match.group(0).split(".")

        return f"{parts[0]}.{parts[1]}.*.*"

    return re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        replace,
        value,
    )


def sanitize_text(value: str) -> str:
    """Apply all supported sensitive-data masking rules."""

    if not value:
        return value

    sanitized = value

    sanitized = mask_email(sanitized)
    sanitized = mask_pan(sanitized)
    sanitized = mask_student_id(sanitized)
    sanitized = mask_phone(sanitized)
    sanitized = mask_ip_address(sanitized)

    return sanitized