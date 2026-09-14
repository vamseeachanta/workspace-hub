"""Bounded, pure evidence comparison. A matching receipt never grants authority."""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
import re

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from evidence_threshold_eligibility import normalize_changed_paths

RESOURCE_SCHEMA = "urn:workspace-hub:resource-descriptor:1"
MAX_BYTES = 1048576
# Canonical schema pins bind supplied validators to this reviewed v1 contract.
SCHEMA_PINS = {
    "urn:workspace-hub:workflow-receipt:1": "6c3c0fc94b16de810819adbc7c88f91cfbd8cc0bbb2bd0e5c36065182804ad13",
    RESOURCE_SCHEMA: "f49294257f3400d5eaaa99c69932405a4118c011b8c7a8fede7346faf5638479",
}


class InvalidReceipt(ValueError):
    def __init__(self, code="RECEIPT_INVALID"):
        super().__init__(code)
        self.code = code


def _bounded(value):
    stack, count = [(value, 0)], 0
    while stack:
        item, depth = stack.pop()
        count += 1
        if depth > 64 or count > 100000:
            raise ValueError("JSON complexity limit")
        if isinstance(item, dict):
            if any(not isinstance(k, str) for k in item):
                raise ValueError("JSON keys must be strings")
            stack.extend((v, depth + 1) for pair in item.items() for v in pair)
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
        elif isinstance(item, str):
            item.encode("utf-8", errors="strict")
        elif isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError("Non-finite JSON number")
        elif item is not None and type(item) not in (int, bool):
            raise ValueError("Unsupported JSON value")


def canonical_bytes(value):
    try:
        _bounded(value)
        result = json.dumps(value, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(result) > MAX_BYTES:
            raise ValueError("JSON byte limit")
        return result
    except (UnicodeError, RecursionError, OverflowError) as exc:
        raise ValueError("Invalid JSON value") from exc


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("Non-finite JSON number")


def load_json(raw, max_bytes=MAX_BYTES):
    try:
        if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
            raise ValueError("Invalid byte limit")
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, bytes) or len(raw) > max_bytes:
            raise ValueError("Invalid or oversized input")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=_nonfinite)
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        canonical_bytes(value)
        return value
    except (UnicodeError, RecursionError, OverflowError) as exc:
        raise ValueError("Invalid JSON input") from exc


def sha256(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def evidence_digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    if not isinstance(value, bytes) or len(value) > MAX_BYTES:
        raise ValueError("Invalid evidence bytes")
    value.decode("utf-8", errors="strict")
    return hashlib.sha256(value).hexdigest()


def _validate(value, schema, resource_schema=None):
    try:
        canonical_bytes(value)
        if not isinstance(schema, dict) or sha256(schema) != SCHEMA_PINS.get(schema.get("$id")):
            raise ValueError("Unrecognized schema contract")
        if resource_schema is not None and sha256(resource_schema) != SCHEMA_PINS[RESOURCE_SCHEMA]:
            raise ValueError("Unrecognized resource contract")
        if "date-time" not in FormatChecker.checkers:
            raise ValueError("RFC3339 checker unavailable")
        registry = Registry()
        if resource_schema is not None:
            registry = registry.with_resource(RESOURCE_SCHEMA, Resource.from_contents(resource_schema))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, registry=registry,
                             format_checker=FormatChecker()).validate(value)
    except Exception as exc:
        raise ValueError("Schema validation failed") from exc


def _instant(value):
    if not isinstance(value, str) or not FormatChecker().conforms(value, "date-time"):
        raise ValueError("Invalid timestamp")
    parsed = datetime.fromisoformat(value.replace("z", "+00:00").replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timezone required")
    return parsed


def _sorted_set(values):
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError("String set required")
    if values != sorted(set(values)):
        raise ValueError("Unsorted or duplicate set")


def _legacy(descriptor):
    observed = descriptor["resource"]["doc_key"]
    projected = descriptor["stable_projection"]["doc_key"]
    if isinstance(observed, str) and re.fullmatch(r"[a-fA-F0-9]{64}", observed):
        evidence = descriptor["identity_evidence"]
        if projected != observed or evidence["original_doc_key"] != observed:
            raise ValueError("Legacy identity evidence mismatch")
        if not evidence["normalization_warning"].strip():
            raise ValueError("Legacy warning required")
        normalized = "sha256:" + observed.lower()
        descriptor["resource"]["doc_key"] = normalized
        descriptor["stable_projection"]["doc_key"] = normalized


def _resource_times(item, as_of):
    now, observed = _instant(as_of), _instant(item["observed_at"])
    if not _instant(item["freshness"]["source_vintage"]) <= observed <= now:
        raise ValueError("Invalid vintage or observation time")
    for stamp in (item["verified_at"], item["rights"]["checked_at"]):
        if _instant(stamp) > now:
            raise ValueError("Future verification")
    for group in ("rights", "freshness"):
        if _instant(item[group]["valid_until"]) <= now:
            raise ValueError("Expired evidence")


def validate_resource(descriptor, schema, *, as_of, source_ids, operation="read",
                      destination="private", legacy_read=False):
    canonical_bytes(descriptor)
    item = deepcopy(descriptor)
    if legacy_read:
        try:
            _legacy(item)
        except (TypeError, KeyError, AttributeError) as exc:
            raise ValueError("Malformed legacy descriptor") from exc
    _validate(item, schema)
    if schema.get("$id") != RESOURCE_SCHEMA or item["schema_version"] != "1":
        raise ValueError("Unknown resource schema")
    if item["readiness_status"] != "ready" or item["source_status"] in (
            "gap", "unreachable", "superseded"):
        raise ValueError("Resource unverified")
    if item["resource"] != item["stable_projection"]:
        raise ValueError("Projection mismatch")
    if not isinstance(source_ids, (list, tuple, set, frozenset)):
        raise ValueError("Catalog context required")
    if item["resource"]["source_id"] not in source_ids:
        raise ValueError("Unknown catalog identity")
    rights = item["rights"]
    if rights["status"] != "permitted" or item["access_status"] != "available":
        raise ValueError("Unavailable rights or access")
    if operation not in rights["operations"] or destination not in rights["destinations"]:
        raise ValueError("Operation or destination not permitted")
    for values in (item["resource"]["derived_from"], rights["operations"], rights["destinations"]):
        _sorted_set(values)
    _resource_times(item, as_of)
    return item


def resource_hashes(descriptor, schema, **context):
    normalized = validate_resource(descriptor, schema, **context)
    return sha256(normalized), sha256(normalized["stable_projection"])


def _paths(paths):
    _sorted_set(paths)
    if normalize_changed_paths(paths) != paths:
        raise ValueError("Non-normalized path")


def _evidence(receipt, artifacts):
    try:
        evidence = receipt["evidence"]
        actual = evidence_digest(artifacts[evidence["locator"]])
        if actual != evidence["evidence_artifact_sha256"]:
            raise ValueError("Evidence changed")
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise InvalidReceipt("EVIDENCE_DIGEST_MISMATCH") from exc


def _resource_bindings(receipt, schema, context):
    hashes = []
    try:
        for wrapper in receipt["resources"]:
            full, stable = resource_hashes(wrapper["descriptor"], schema, **context)
            if full != wrapper["resource_descriptor_sha256"] or stable != wrapper["resource_stable_sha256"]:
                raise ValueError("Resource digest mismatch")
            hashes.append(stable)
        if len(hashes) != len(set(hashes)):
            raise ValueError("Duplicate resource")
        if sorted(hashes) != receipt["key"]["resource_stable_sha256s"]:
            raise ValueError("Resource key mismatch")
    except (ValueError, TypeError, KeyError) as exc:
        raise InvalidReceipt("RESOURCE_UNVERIFIED") from exc


def _receipt(item, workflow_schema, resource_schema, as_of, context, artifacts):
    _validate(item, workflow_schema, resource_schema)
    if _instant(item["observed_at"]) > _instant(as_of):
        raise InvalidReceipt()
    _paths(item["key"]["changed_paths"])
    _sorted_set(item["key"]["resource_stable_sha256s"])
    if sha256(item["key"]) != item["key_sha256"]:
        raise InvalidReceipt()
    _evidence(item, artifacts)
    _resource_bindings(item, resource_schema, dict(context, as_of=as_of))


def compare_receipts(previous, current, *, workflow_schema, resource_schema=None,
                     as_of, source_ids, evidence_artifacts, resource_operation="read",
                     destination="private"):
    """Compare supplied claims; live permission/provenance validation remains mandatory."""
    try:
        canonical_bytes(previous)
        canonical_bytes(current)
        if canonical_bytes(previous["key"]) != canonical_bytes(current["key"]):
            raise InvalidReceipt("KEY_CHANGED")
        if resource_schema is None and any(r.get("resources") for r in (previous, current)):
            return {"reuse_assessment": "needs-context", "reason_codes": ["SCHEMA_UNAVAILABLE"]}
        context = {"source_ids": source_ids, "operation": resource_operation, "destination": destination}
        _receipt(previous, workflow_schema, resource_schema, previous["observed_at"], context,
                 evidence_artifacts)
        _receipt(current, workflow_schema, resource_schema, as_of, context, evidence_artifacts)
        if _instant(previous["observed_at"]) > _instant(as_of):
            raise InvalidReceipt()
        return {"reuse_assessment": "candidate-pending-live-validation",
                "reason_codes": ["MUTABLE_VALIDATION_REQUIRED"]}
    except InvalidReceipt as exc:
        return {"reuse_assessment": "invalid", "reason_codes": [exc.code]}
    except Exception:
        return {"reuse_assessment": "invalid", "reason_codes": ["RECEIPT_INVALID"]}
