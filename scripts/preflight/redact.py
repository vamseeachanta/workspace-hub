"""Redaction helpers for workstation preflight output."""

from __future__ import annotations

import re


GH_TOKEN_RE = re.compile(r"\bgh[opsu]_[A-Za-z0-9_]{20,}")
JWT_RE = re.compile(
    r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"
)
API_KEY_RE = re.compile(r"\b(?:sk|pk|api)[_-][A-Za-z0-9]{20,}")
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}", re.IGNORECASE)


def redact_text(value: object) -> str:
    """Return a string with known secret shapes removed."""

    text = "" if value is None else str(value)
    text = GH_TOKEN_RE.sub("[REDACTED:gh-token]", text)
    text = JWT_RE.sub("[REDACTED:jwt]", text)
    text = API_KEY_RE.sub("[REDACTED:api-key]", text)
    text = BEARER_RE.sub("Bearer [REDACTED:bearer-token]", text)
    return text


def strip_url_secret(url: str) -> str:
    """Drop query strings/fragments from provider URLs before reporting."""

    for marker in ("?", "#"):
        if marker in url:
            url = url.split(marker, 1)[0]
    return redact_text(url)

