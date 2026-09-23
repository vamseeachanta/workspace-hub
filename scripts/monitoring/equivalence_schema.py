"""Exact schema validation for machine-equivalence fingerprints."""
from __future__ import annotations

from datetime import datetime
import json
import math
import re

FINGERPRINT_KEYS = {
    "fingerprint_version", "role", "hostname", "machine_id", "ts", "clone_head",
    "behind_origin", "ahead_origin", "harness_version", "harness_install",
    "registry_sha256", "learning_cron_ages_h", "provider_soul_hashes", "on_main",
    "index_lock_stale_min", "last_publish_duration_s",
}
ROLES = {"full", "contribute", "contribute-minimal", "unknown"}
LEARNING_KEYS = {"comprehensive-learning-nightly", "session-analysis"}
PROVIDER_KEYS = {"hermes", "claude", "codex", "codex_agents", "gemini"}
MACHINE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
HEX_RE = re.compile(r"^[0-9a-f]+$")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class FingerprintValidationError(ValueError):
    pass


def _reject_constant(value):
    raise FingerprintValidationError(f"non-finite JSON constant: {value}")


def _require_text(value, field):
    if not isinstance(value, str) or not value or any(ord(char) < 32 for char in value):
        raise FingerprintValidationError(f"{field} must be nonempty control-free text")


def _require_optional_number(value, field):
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FingerprintValidationError(f"{field} must be null or numeric")
    if not math.isfinite(value) or value < 0:
        raise FingerprintValidationError(f"{field} must be finite and nonnegative")


def _require_optional_hex(value, field, lengths):
    if value is None:
        return
    if not isinstance(value, str) or len(value) not in lengths or not HEX_RE.fullmatch(value):
        raise FingerprintValidationError(f"{field} has invalid hexadecimal value")


def require_rfc3339(value, field="ts"):
    if not isinstance(value, str) or not RFC3339_RE.fullmatch(value):
        raise FingerprintValidationError(f"{field} must be an RFC3339 string")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FingerprintValidationError(f"{field} must be valid RFC3339") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise FingerprintValidationError(f"{field} must include a timezone offset")
    return stamp


def _validate_identity_and_time(data):
    if not isinstance(data["role"], str) or data["role"] not in ROLES:
        raise FingerprintValidationError("role is outside the version-1 enum")
    _require_text(data["hostname"], "hostname")
    _require_text(data["machine_id"], "machine_id")
    if not MACHINE_RE.fullmatch(data["machine_id"]):
        raise FingerprintValidationError("machine_id is unsafe")
    require_rfc3339(data["ts"])


def _validate_telemetry(data):
    _require_optional_hex(data["clone_head"], "clone_head", range(7, 41))
    for field in ("behind_origin", "ahead_origin"):
        value = data[field]
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise FingerprintValidationError(f"{field} must be null or a nonnegative integer")
    for field in ("harness_version", "harness_install"):
        if data[field] is not None:
            _require_text(data[field], field)
    _require_optional_hex(data["registry_sha256"], "registry_sha256", {64})
    learning = data["learning_cron_ages_h"]
    if not isinstance(learning, dict) or set(learning) != LEARNING_KEYS:
        raise FingerprintValidationError("learning_cron_ages_h has invalid keys")
    for key, value in learning.items():
        _require_optional_number(value, f"learning_cron_ages_h.{key}")
    providers = data["provider_soul_hashes"]
    if not isinstance(providers, dict) or set(providers) != PROVIDER_KEYS:
        raise FingerprintValidationError("provider_soul_hashes has invalid keys")
    for key, value in providers.items():
        _require_optional_hex(value, f"provider_soul_hashes.{key}", {16})
    if not isinstance(data["on_main"], bool):
        raise FingerprintValidationError("on_main must be boolean")
    _require_optional_number(data["index_lock_stale_min"], "index_lock_stale_min")
    _require_optional_number(data["last_publish_duration_s"], "last_publish_duration_s")


def validate_fingerprint(content):
    try:
        data = json.loads(content, parse_constant=_reject_constant)
    except (json.JSONDecodeError, TypeError) as exc:
        raise FingerprintValidationError(f"invalid fingerprint JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) != FINGERPRINT_KEYS:
        raise FingerprintValidationError("fingerprint must contain the exact version-1 key set")
    version = data["fingerprint_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise FingerprintValidationError("fingerprint_version must be integer 1")
    _validate_identity_and_time(data)
    _validate_telemetry(data)
    return data
