"""Strict semantic validation for legal rule-authority documents."""

from __future__ import annotations

import base64
import binascii
import re
import uuid
from collections.abc import Callable

MAX_U64 = (1 << 64) - 1
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")


class ModelError(ValueError):
    """Document violates its closed schema or semantic constraints."""


def _keys(value: object, expected: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise ModelError("invalid document fields")
    return value


def _u64(value: object, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value <= MAX_U64:
        raise ModelError("invalid unsigned integer")
    return value


def _uuid4(value: object) -> str:
    if not isinstance(value, str):
        raise ModelError("invalid revision")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ModelError("invalid revision") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise ModelError("invalid revision")
    return value


def _hex64(value: object) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise ModelError("invalid digest")
    return value


def _schema(value: object, expected: str) -> None:
    if value != expected:
        raise ModelError("invalid schema")


def _rules_sorted(rules: object) -> list[dict]:
    if not isinstance(rules, list) or not rules:
        raise ModelError("rules must be nonempty")
    ids = [_uuid4(rule.get("rule_id") if isinstance(rule, dict) else None) for rule in rules]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ModelError("rules must have sorted unique IDs")
    return rules


def validate_registry(value: object) -> None:
    doc = _keys(value, {"authority_revision", "generation", "rules", "schema_id"})
    _schema(doc["schema_id"], "legal-rule-registry-v1")
    _uuid4(doc["authority_revision"])
    _u64(doc["generation"], 1)
    for rule in _rules_sorted(doc["rules"]):
        item = _keys(rule, {"match_mode", "rule_id", "severity", "target"})
        if item["match_mode"] not in {"exact-bytes", "ascii-fold"}:
            raise ModelError("invalid match mode")
        if item["severity"] not in {"block", "warn"}:
            raise ModelError("invalid severity")
        if item["target"] not in {"path", "content", "both"}:
            raise ModelError("invalid target")


def _prefix(value: object) -> str:
    if not isinstance(value, str) or not value or not value.isascii() or not value.endswith("/"):
        raise ModelError("invalid forensic prefix")
    parts = value[:-1].split("/")
    if value.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise ModelError("invalid forensic prefix")
    return value


def validate_policy(value: object) -> None:
    fields = {"authority_revision", "forensic_prefixes", "generation", "limits", "schema_id"}
    doc = _keys(value, fields)
    _schema(doc["schema_id"], "legal-rule-policy-v1")
    _uuid4(doc["authority_revision"])
    _u64(doc["generation"], 1)
    prefixes = doc["forensic_prefixes"]
    if not isinstance(prefixes, list):
        raise ModelError("invalid prefixes")
    checked = [_prefix(prefix) for prefix in prefixes]
    if checked != sorted(checked) or len(checked) != len(set(checked)):
        raise ModelError("prefixes must be sorted and unique")
    limits = _keys(doc["limits"], {"max_blob_bytes", "max_entries", "max_findings", "max_request_bytes"})
    _bounded_limits(limits)


def _bounded_limits(limits: dict) -> None:
    bounds = {
        "max_blob_bytes": 10_485_760,
        "max_entries": 10_000,
        "max_findings": 1_000,
        "max_request_bytes": 104_857_600,
    }
    for name, maximum in bounds.items():
        if not 1 <= _u64(limits[name], 1) <= maximum:
            raise ModelError("limit out of range")


def _pattern(value: object) -> bytes:
    if not isinstance(value, str) or not value.isascii():
        raise ModelError("invalid pattern encoding")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ModelError("invalid pattern encoding") from exc
    if base64.b64encode(decoded).decode("ascii") != value or not 1 <= len(decoded) <= 16_384:
        raise ModelError("invalid pattern encoding")
    return decoded


def validate_map(value: object) -> None:
    doc = _keys(value, {"authority_revision", "generation", "rules", "schema_id"})
    _schema(doc["schema_id"], "legal-rule-map-v1")
    _uuid4(doc["authority_revision"])
    _u64(doc["generation"], 1)
    decoded = []
    for rule in _rules_sorted(doc["rules"]):
        item = _keys(rule, {"pattern_b64", "rule_id"})
        decoded.append(_pattern(item["pattern_b64"]))
    if sum(map(len, decoded)) > 16_384 or len(decoded) != len(set(decoded)):
        raise ModelError("duplicate or oversized patterns")


def validate_manifest(value: object) -> None:
    fields = {"authority_revision", "generation", "manifest_mac", "map_sha256",
              "policy_sha256", "registry_sha256", "schema_id"}
    doc = _keys(value, fields)
    _schema(doc["schema_id"], "legal-rule-authority-manifest-v1")
    _uuid4(doc["authority_revision"])
    _u64(doc["generation"], 1)
    for field in fields - {"authority_revision", "generation", "schema_id"}:
        _hex64(doc[field])


def validate_anchor(value: object) -> None:
    fields = {"authority_revision", "expected_head_oid", "generation", "manifest_mac",
              "schema_id", "slot", "tool_sha"}
    doc = _keys(value, fields)
    _schema(doc["schema_id"], "legal-rule-active-anchor-v1")
    _uuid4(doc["authority_revision"])
    _u64(doc["generation"], 1)
    _hex64(doc["manifest_mac"])
    if doc["slot"] not in {"current", "pending"}:
        raise ModelError("invalid slot")
    if not isinstance(doc["tool_sha"], str) or OID.fullmatch(doc["tool_sha"]) is None:
        raise ModelError("invalid tool OID")
    head = doc["expected_head_oid"]
    if head is not None and (not isinstance(head, str) or OID.fullmatch(head) is None):
        raise ModelError("invalid head OID")


def validate_ledger(value: object) -> None:
    doc = _keys(value, {"entries", "key_id", "ledger_mac", "schema_id"})
    _schema(doc["schema_id"], "legal-rule-generation-ledger-v1")
    if not isinstance(doc["key_id"], str) or not doc["key_id"].isascii() or not doc["key_id"]:
        raise ModelError("invalid key ID")
    _hex64(doc["ledger_mac"])
    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        raise ModelError("ledger must be nonempty")
    generations = []
    revisions = []
    for entry in entries:
        item = _keys(entry, {"authority_revision", "generation", "manifest_mac"})
        generations.append(_u64(item["generation"], 1))
        revisions.append(_uuid4(item["authority_revision"]))
        _hex64(item["manifest_mac"])
    if generations != sorted(generations) or len(generations) != len(set(generations)):
        raise ModelError("ledger generations must be sorted and unique")
    if len(revisions) != len(set(revisions)):
        raise ModelError("ledger revisions must be unique")


VALIDATORS: dict[str, Callable[[object], None]] = {
    "registry": validate_registry,
    "policy": validate_policy,
    "map": validate_map,
    "manifest": validate_manifest,
    "anchor": validate_anchor,
    "ledger": validate_ledger,
}


def validate_document(kind: str, value: object) -> None:
    try:
        validator = VALIDATORS[kind]
    except KeyError as exc:
        raise ModelError("unknown document kind") from exc
    validator(value)
