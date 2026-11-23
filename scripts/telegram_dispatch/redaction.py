"""Secret redaction helpers for Telegram/Hermes dispatch status."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTION = "[REDACTED]"

SECRET_KEY_RE = re.compile(r"(token|secret|api[_-]?key|password|credential)", re.IGNORECASE)
TELEGRAM_PRIVATE_KEY_RE = re.compile(r"(allowed_?user_?ids?|chat_?id|invite_?link|phone(_?number)?)", re.IGNORECASE)
TELEGRAM_TOKEN_RE = re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{5,}\b")
API_KEY_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]+|gh[pousr]_[A-Za-z0-9_]{10,}|[A-Za-z0-9_]{32,})\b")
TELEGRAM_CHAT_ID_VALUE_RE = re.compile(r"(?i)(chat_?id\s*[:=]\s*)\-?\d{6,}")
TELEGRAM_ALLOWLIST_VALUE_RE = re.compile(r"(?i)((?:allowlist|allowed[_-]?user[_-]?ids?)\s*[:=]\s*)[0-9,\s]+")
TELEGRAM_INVITE_LINK_RE = re.compile(r"https://t\.me/\+[A-Za-z0-9_-]+")
PHONE_VALUE_RE = re.compile(r"(?i)(?:phone(?:_?number)?\s*[:=]\s*\+?\d[\d\-()\s*]{4,}\d|\+\d[\d\-()\s*]{4,}\d)")
CONTEXTUAL_TOKEN_FRAGMENT_RE = re.compile(
    r"(?i)(\b(?:bot\s+)?token\s+(?:tail|fragment)\s+)([A-Za-z0-9_-]{4,})"
)
REMOTE_FRAGMENT_VALUE_RE = re.compile(r"(?i)(\bfragment\s+)([A-Za-z0-9_-]{4,})")
TOKEN_FRAGMENT_DENYLIST = {"fail", "host", "http", "tion", "reda", "acte", "cted"}
SAFE_ENV_POINTERS = ("TELEGRAM_HERMES_ALLOWED_USER_IDS", "TELEGRAM_HERMES_BOT_TOKEN")


def _redact_string(value: str) -> str:
    env_placeholders: dict[str, str] = {}
    for index, env_name in enumerate(SAFE_ENV_POINTERS):
        placeholder = f"__HERMES_SAFE_ENV_POINTER_{index}__"
        if env_name in value:
            value = value.replace(env_name, placeholder)
            env_placeholders[placeholder] = env_name
    value = TELEGRAM_TOKEN_RE.sub(REDACTION, value)
    value = API_KEY_RE.sub(REDACTION, value)
    value = TELEGRAM_CHAT_ID_VALUE_RE.sub(r"\1" + REDACTION, value)
    value = TELEGRAM_ALLOWLIST_VALUE_RE.sub(r"\1" + REDACTION, value)
    value = TELEGRAM_INVITE_LINK_RE.sub(REDACTION, value)
    value = PHONE_VALUE_RE.sub(REDACTION, value)
    value = CONTEXTUAL_TOKEN_FRAGMENT_RE.sub(r"\1" + REDACTION, value)
    value = REMOTE_FRAGMENT_VALUE_RE.sub(r"\1" + REDACTION, value)
    for placeholder, env_name in env_placeholders.items():
        value = value.replace(placeholder, env_name)
    return value


def redact_status(payload: Any) -> Any:
    """Return a copy of *payload* with secret-like fields and values removed."""
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text) or TELEGRAM_PRIVATE_KEY_RE.search(key_text):
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


def _redact_token_material(value: str, token: str) -> str:
    """Redact a supplied Telegram token and recognizable token fragments."""
    redacted = value.replace(token, REDACTION)
    if ":" not in token:
        return redacted
    bot_id, secret = token.split(":", 1)
    if len(bot_id) >= 6:
        redacted = redacted.replace(bot_id, REDACTION)
    if len(secret) >= 4:
        redacted = redacted.replace(secret, REDACTION)
        for start in range(0, max(len(secret) - 3, 0), 4):
            fragment = secret[start : start + 4]
            if len(fragment) >= 4 and fragment.lower() not in TOKEN_FRAGMENT_DENYLIST:
                redacted = redacted.replace(fragment, REDACTION)
    return redacted


def format_token_validation_failure(token: str, *, reason: str) -> str:
    """Format token validation errors without echoing token material."""
    safe_reason = _redact_token_material(_redact_string(reason), token)
    return f"Telegram bot token validation failed: {safe_reason}; token={REDACTION}"
