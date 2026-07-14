"""Strict canonical JSON codec for authority documents."""

from __future__ import annotations

import json

from .models import ModelError, validate_document

MAXIMUMS = {
    "registry": 2 * 1024 * 1024,
    "policy": 2 * 1024 * 1024,
    "map": 24 * 1024,
    "manifest": 2 * 1024 * 1024,
    "anchor": 2 * 1024,
    "ledger": 2 * 1024 * 1024,
    "complete": 2 * 1024 * 1024,
}


class AuthorityFormatError(ValueError):
    """Input is not a valid canonical authority document."""


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuthorityFormatError("duplicate JSON key")
        result[key] = value
    return result


def _constant(_value: str):
    raise AuthorityFormatError("non-finite number")


def canonical_bytes(value: object) -> bytes:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AuthorityFormatError("not JSON encodable") from exc
    return (text + "\n").encode("ascii")


def encode_document(kind: str, value: object) -> bytes:
    try:
        validate_document(kind, value)
        encoded = canonical_bytes(value)
        maximum = MAXIMUMS[kind]
    except (KeyError, ModelError) as exc:
        raise AuthorityFormatError("invalid authority document") from exc
    if len(encoded) > maximum:
        raise AuthorityFormatError("authority document too large")
    return encoded


def decode_document(kind: str, raw: bytes) -> dict:
    if not isinstance(raw, bytes) or not raw.endswith(b"\n"):
        raise AuthorityFormatError("canonical document requires one LF")
    if len(raw) > MAXIMUMS.get(kind, 0) or raw.startswith(b"\xef\xbb\xbf"):
        raise AuthorityFormatError("invalid authority bytes")
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant,
                           parse_float=lambda _value: _constant("float"))
        encoded = encode_document(kind, value)
    except (UnicodeDecodeError, json.JSONDecodeError, AuthorityFormatError) as exc:
        raise AuthorityFormatError("invalid authority bytes") from exc
    if encoded != raw:
        raise AuthorityFormatError("document is not canonical")
    return value
