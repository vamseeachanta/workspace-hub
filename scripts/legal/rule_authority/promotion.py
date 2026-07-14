"""Owner-only Phase-B compare-and-swap precondition validation."""

from __future__ import annotations

import hashlib
import os
import re

from .codec import AuthorityError, parse_canonical


OID = re.compile(r"[0-9a-f]{40}")


def validate(current_name, pending_name, expected_head, expected_tree, preview_bytes):
    """Validate a promotion descriptor without exposing or mutating envelopes."""
    if (
        os.environ.get("GITHUB_ACTIONS")
        or os.environ.get("LEGAL_RULE_OWNER_PROMOTE") != "1"
    ):
        raise AuthorityError("config")
    if not OID.fullmatch(expected_head) or not OID.fullmatch(expected_tree):
        raise AuthorityError("config")
    current = os.environ.get(current_name)
    pending = os.environ.get(pending_name)
    if not current or not pending or current_name == pending_name:
        raise AuthorityError("config")
    preview = parse_canonical(preview_bytes)
    required = {
        "current_envelope_sha256",
        "expected_head_oid",
        "expected_tree_oid",
        "pending_envelope_sha256",
        "schema_id",
    }
    if not isinstance(preview, dict) or set(preview) != required:
        raise AuthorityError("schema")
    actual = {
        "current_envelope_sha256": hashlib.sha256(current.encode("ascii")).hexdigest(),
        "expected_head_oid": expected_head,
        "expected_tree_oid": expected_tree,
        "pending_envelope_sha256": hashlib.sha256(pending.encode("ascii")).hexdigest(),
        "schema_id": "legal-rule-promotion-preview-v1",
    }
    if actual != preview:
        raise AuthorityError("integrity")
    return actual
