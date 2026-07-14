"""Authenticated COMPLETE transaction manifests."""

from __future__ import annotations

import hashlib
import hmac

from .codec import canonical_bytes, decode_document, encode_document

COMPLETE_DOMAIN = b"LEGAL-RULE-COMPLETE\0v1\0"


class CompleteIntegrityError(ValueError):
    """A COMPLETE transaction failed authentication."""


def _require_key(key: bytes) -> None:
    """Require an exact 32-byte COMPLETE authentication key."""
    if type(key) is not bytes or len(key) != 32:
        raise CompleteIntegrityError("invalid key")


def complete_mac_input(unsigned: dict) -> bytes:
    """Return domain-separated bytes for a COMPLETE document without its MAC."""
    if "complete_mac" in unsigned:
        raise CompleteIntegrityError("complete MAC input must be unsigned")
    return COMPLETE_DOMAIN + canonical_bytes(unsigned)


def create_complete(unsigned: dict, key: bytes) -> dict:
    """Create a strict authenticated COMPLETE document."""
    _require_key(key)
    document = dict(unsigned)
    document["complete_mac"] = "0" * 64
    encode_document("complete", document)
    document["complete_mac"] = hmac.new(
        key, complete_mac_input(unsigned), hashlib.sha256).hexdigest()
    return document


def verify_complete(raw: bytes, key: bytes) -> dict:
    """Decode and authenticate a COMPLETE document."""
    _require_key(key)
    document = decode_document("complete", raw)
    unsigned = {name: value for name, value in document.items() if name != "complete_mac"}
    expected = hmac.new(key, complete_mac_input(unsigned), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, document["complete_mac"]):
        raise CompleteIntegrityError("COMPLETE authentication failed")
    return document
