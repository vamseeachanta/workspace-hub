"""Secret redaction helpers for Telegram/Hermes dispatch status."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTION = "[REDACTED]"

SECRET_KEY_RE = re.compile(r"(token|secret|api[_-]?key|password|credential)", re.IGNORECASE)
TELEGRAM_TOKEN_RE = re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")
API_KEY_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]+|[A-Za-z0-9_-]{32,})\b")


def _redact_string(value: str) -> str:
    value = TELEGRAM_TOKEN_RE.sub(REDACTION, value)
    value = API_KEY_RE.sub(REDACTION, value)
    return value


def redact_status(payload: Any) -> Any:
    """Return a copy of *payload* with secret-like fields and values removed."""
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text):
                redacted[key_text] = REDACTION
            else:
                redacted[key_text] = redact_status(value)
        return redacted
    if isinstance(payload, str):
        return _redact_string(payload)
    if isinstance(payload, Sequence) and not isinstance(payload, (bytes, bytearray)):
        return [redact_status(item) for item in payload]
    return payload


def render_status(payload: Any) -> str:
    """Render a redacted status payload for Telegram/GitHub output."""
    return json.dumps(redact_status(payload), sort_keys=True, indent=2, default=str)


def format_token_validation_failure(token: str, *, reason: str) -> str:
    """Format token validation errors without echoing token material."""
    _ = token
    return f"Telegram bot token validation failed: {reason}; token={REDACTION}"
