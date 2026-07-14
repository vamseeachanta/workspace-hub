"""Strict canonical legal-json-v1 codecs. Errors intentionally withhold values."""
from __future__ import annotations

import base64
import json
import re
import uuid


MAX_DOC = 2 * 1024 * 1024
MAX_MAP = 24 * 1024
HEX64 = re.compile(r"[0-9a-f]{64}")
OID = re.compile(r"[0-9a-f]{40,64}")


class AuthorityError(ValueError):
    """Fixed-category error that never embeds private input."""


def canonical_bytes(value: object) -> bytes:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AuthorityError("schema") from exc
    return encoded.encode("ascii") + b"\n"


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuthorityError("schema")
        result[key] = value
    return result


def parse_canonical(data: bytes, maximum: int = MAX_DOC):
    if not isinstance(data, bytes) or not data or len(data) > maximum or data.startswith(b"\xef\xbb\xbf"):
        raise AuthorityError("schema")
    try:
        text = data.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_float=lambda _: (_ for _ in ()).throw(AuthorityError("schema")))
    except (UnicodeError, json.JSONDecodeError, AuthorityError) as exc:
        raise AuthorityError("schema") from exc
    if canonical_bytes(value) != data:
        raise AuthorityError("schema")
    return value


def _exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise AuthorityError("schema")


def _uuid4(value):
    try:
        parsed = uuid.UUID(value)
    except (ValueError, TypeError, AttributeError) as exc:
        raise AuthorityError("schema") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise AuthorityError("schema")


def _generation(value):
    if type(value) is not int or not 1 <= value <= (2**64 - 1):
        raise AuthorityError("schema")


def parse_registry(data: bytes):
    value = parse_canonical(data)
    _exact_keys(value, {"authority_revision", "generation", "rules", "schema_id"})
    if value["schema_id"] != "legal-rule-registry-v1" or not isinstance(value["rules"], list) or not value["rules"]:
        raise AuthorityError("schema")
    _uuid4(value["authority_revision"]); _generation(value["generation"])
    ids = []
    for rule in value["rules"]:
        _exact_keys(rule, {"match_mode", "rule_id", "severity", "target"}); _uuid4(rule["rule_id"])
        if rule["match_mode"] not in {"exact-bytes", "ascii-fold"} or rule["severity"] not in {"block", "warn"} or rule["target"] not in {"path", "content", "both"}:
            raise AuthorityError("schema")
        ids.append(rule["rule_id"])
    if ids != sorted(ids) or len(ids) != len(set(ids)): raise AuthorityError("schema")
    return value


def _prefix(value):
    if not isinstance(value, str) or not value.isascii() or not value.endswith("/") or value.startswith("/"):
        raise AuthorityError("schema")
    if any(part in {"", ".", ".."} for part in value[:-1].split("/")): raise AuthorityError("schema")


def parse_policy(data: bytes):
    value = parse_canonical(data); _exact_keys(value, {"authority_revision", "forensic_prefixes", "generation", "limits", "schema_id"})
    if value["schema_id"] != "legal-rule-policy-v1": raise AuthorityError("schema")
    _uuid4(value["authority_revision"]); _generation(value["generation"])
    prefixes = value["forensic_prefixes"]
    if not isinstance(prefixes, list): raise AuthorityError("schema")
    for prefix in prefixes: _prefix(prefix)
    if prefixes != sorted(prefixes) or len(prefixes) != len(set(prefixes)): raise AuthorityError("schema")
    _exact_keys(value["limits"], {"max_blob_bytes", "max_entries", "max_findings", "max_request_bytes"})
    bounds = {"max_blob_bytes": 10485760, "max_entries": 10000, "max_findings": 1000, "max_request_bytes": 104857600}
    if any(type(value["limits"][key]) is not int or not 1 <= value["limits"][key] <= top for key, top in bounds.items()): raise AuthorityError("schema")
    return value


def parse_map(data: bytes, registry: dict):
    value = parse_canonical(data, MAX_MAP); _exact_keys(value, {"authority_revision", "generation", "rules", "schema_id"})
    if value["schema_id"] != "legal-rule-map-v1" or (value["authority_revision"], value["generation"]) != (registry["authority_revision"], registry["generation"]): raise AuthorityError("schema")
    expected = {item["rule_id"]: item for item in registry["rules"]}; decoded = []
    for rule in value["rules"]:
        _exact_keys(rule, {"pattern_b64", "rule_id"})
        try: pattern = base64.b64decode(rule["pattern_b64"], validate=True)
        except Exception as exc: raise AuthorityError("schema") from exc
        if base64.b64encode(pattern).decode("ascii") != rule["pattern_b64"] or not 1 <= len(pattern) <= 16384 or rule["rule_id"] not in expected: raise AuthorityError("schema")
        if expected[rule["rule_id"]]["match_mode"] == "ascii-fold" and any(byte > 127 for byte in pattern): raise AuthorityError("schema")
        decoded.append((rule["rule_id"], pattern))
    if [x[0] for x in decoded] != sorted(expected) or len({x[1] for x in decoded}) != len(expected): raise AuthorityError("schema")
    return value


def parse_manifest(data: bytes):
    value = parse_canonical(data); _exact_keys(value, {"authority_revision", "generation", "manifest_mac", "map_sha256", "policy_sha256", "registry_sha256", "schema_id"})
    if value["schema_id"] != "legal-rule-authority-manifest-v1": raise AuthorityError("schema")
    _uuid4(value["authority_revision"]); _generation(value["generation"])
    if any(not HEX64.fullmatch(value[key]) for key in ("manifest_mac", "map_sha256", "policy_sha256", "registry_sha256")): raise AuthorityError("schema")
    return value


def parse_anchor(data: bytes):
    value = parse_canonical(data, 2048); _exact_keys(value, {"authority_revision", "generation", "manifest_mac", "schema_id", "slot", "tool_sha", "expected_head_oid"})
    if value["schema_id"] != "legal-rule-active-anchor-v1" or value["slot"] not in {"current", "pending"}: raise AuthorityError("schema")
    _uuid4(value["authority_revision"]); _generation(value["generation"])
    if not HEX64.fullmatch(value["manifest_mac"]) or not OID.fullmatch(value["tool_sha"]): raise AuthorityError("schema")
    if value["expected_head_oid"] is not None and not OID.fullmatch(value["expected_head_oid"]): raise AuthorityError("schema")
    return value
