"""Owner-only Phase-B compare-and-swap precondition validation."""

from __future__ import annotations

import hashlib
import os
import re

from .codec import AuthorityError, parse_canonical


OID = re.compile(r"[0-9a-f]{40}")


def _owner_gate():
    if (
        os.environ.get("GITHUB_ACTIONS")
        or os.environ.get("LEGAL_RULE_OWNER_PROMOTE") != "1"
    ):
        raise AuthorityError("config")


def _validate_values(current, pending, expected_head, expected_tree, preview_bytes):
    if (
        not isinstance(expected_head, str)
        or not isinstance(expected_tree, str)
        or not OID.fullmatch(expected_head)
        or not OID.fullmatch(expected_tree)
    ):
        raise AuthorityError("config")
    if not isinstance(current, str) or not isinstance(pending, str):
        raise AuthorityError("config")
    if not current or not pending:
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
        "current_envelope_sha256": _digest(current),
        "expected_head_oid": expected_head,
        "expected_tree_oid": expected_tree,
        "pending_envelope_sha256": _digest(pending),
        "schema_id": "legal-rule-promotion-preview-v1",
    }
    if actual != preview:
        raise AuthorityError("integrity")
    return actual


def _digest(value):
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise AuthorityError("config") from exc
    return hashlib.sha256(encoded).hexdigest()


def validate(current_name, pending_name, expected_head, expected_tree, preview_bytes):
    """Validate a promotion descriptor without exposing or mutating envelopes."""
    _owner_gate()
    if current_name == pending_name:
        raise AuthorityError("config")
    return _validate_values(
        os.environ.get(current_name),
        os.environ.get(pending_name),
        expected_head,
        expected_tree,
        preview_bytes,
    )


def _read_main(api):
    value = api.read_main()
    if not isinstance(value, dict) or set(value) != {"head_oid", "tree_oid"}:
        raise AuthorityError("integrity")
    if (
        not isinstance(value["head_oid"], str)
        or not isinstance(value["tree_oid"], str)
        or not OID.fullmatch(value["head_oid"])
        or not OID.fullmatch(value["tree_oid"])
    ):
        raise AuthorityError("integrity")
    return value


def promote(
    api, current_name, pending_name, expected_head, expected_tree, preview_bytes
):
    """Run an owner-only, dependency-injected slot promotion transaction.

    The caller supplies the transport. This module intentionally contains no live
    HTTP implementation, credentials, endpoint names, or implicit retries.
    """
    _owner_gate()
    if current_name == pending_name:
        raise AuthorityError("config")

    current = api.read_slot(current_name)
    pending = api.read_slot(pending_name)
    expected = _validate_values(
        current, pending, expected_head, expected_tree, preview_bytes
    )
    if _read_main(api) != {
        "head_oid": expected_head,
        "tree_oid": expected_tree,
    }:
        raise AuthorityError("integrity")

    # The second reads are the compare step immediately before the only write.
    if api.read_slot(current_name) != current or api.read_slot(pending_name) != pending:
        raise AuthorityError("integrity")
    api.write_slot(current_name, pending)

    # Retain PENDING on any post-write failure so recovery remains owner-directed.
    if api.read_slot(current_name) != pending:
        raise AuthorityError("integrity")
    if _read_main(api) != {
        "head_oid": expected_head,
        "tree_oid": expected_tree,
    }:
        raise AuthorityError("integrity")
    if api.read_slot(pending_name) != pending:
        raise AuthorityError("integrity")
    api.delete_slot(pending_name)
    return expected
