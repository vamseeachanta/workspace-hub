#!/usr/bin/env python3
"""Pure shared workflow assessment; JSON references never grant authority."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from evidence_threshold_eligibility import (
    ELIGIBLE_CLASSES, INELIGIBLE_CLASSES, classify, default_config, evaluate_eligibility,
    normalize_changed_paths,
)
from workflow_receipt import compare_receipts, load_json

MAX_BYTES = 1048576
CONSEQUENTIAL = {"publication", "destruction", "access-change", "engineering-basis-change"}
EFFECTS = CONSEQUENTIAL | {"read-only", "local-reversible", "substantial-change"}
FIELDS = {"schema_version", "provider", "operation_kind", "scope", "changed_paths",
          "effects", "authorization_reference", "metrics", "reuse"}


def _unknown():
    return {"risk_class": "unknown", "authorization_assessment": "missing",
            "action_boundary": "needs-context", "metric_advice": "not-requested",
            "reuse_assessment": "not-requested", "reason_codes": ["MISSING_CONTEXT"]}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 4096


def _context(request):
    if not isinstance(request, dict) or set(request) - FIELDS:
        raise ValueError("invalid request fields")
    if request.get("schema_version") != "1":
        raise ValueError("unknown version")
    if "provider" in request and not _nonempty(request["provider"]):
        raise ValueError("invalid provider metadata")
    scope = request.get("scope")
    names = {"repository_id", "task_id", "operation_id", "bounded"}
    if not isinstance(scope, dict) or set(scope) != names or scope["bounded"] is not True:
        raise ValueError("unbounded scope")
    if any(not _nonempty(scope[name]) for name in names - {"bounded"}):
        raise ValueError("missing scope identity")
    paths = normalize_changed_paths(request.get("changed_paths"))
    effects = request.get("effects")
    if (not isinstance(effects, list) or not effects
            or any(not isinstance(e, str) for e in effects) or len(effects) != len(set(effects))):
        raise ValueError("invalid effects")
    reference = request.get("authorization_reference")
    if reference is not None and not _nonempty(reference):
        raise ValueError("invalid reference")
    return scope, paths, set(effects), reference


def _operation(request, paths, effects, reference):
    result = _unknown()
    result["authorization_assessment"] = "unverified-reference" if reference else "missing"
    reasons = ["UNVERIFIED_AUTHORITY"] if reference else []
    kind = request.get("operation_kind")
    issue_class = classify(paths, [])
    if not isinstance(kind, str) or kind not in {"inspect", "edit", "execute"} or effects - EFFECTS:
        result["reason_codes"] = reasons + ["UNKNOWN_EFFECT"]
    elif kind == "inspect" and (effects != {"read-only"} or paths):
        result["reason_codes"] = reasons + ["MISSING_CONTEXT"]
    elif kind == "inspect":
        result.update(risk_class="read-only", action_boundary="assessment-only",
                      authorization_assessment="not-required-for-assessment",
                      reason_codes=["READ_ONLY_ASSESSMENT"])
    elif "read-only" in effects or (kind == "edit" and not paths):
        result["reason_codes"] = reasons + ["MISSING_CONTEXT"]
    elif effects & CONSEQUENTIAL:
        result.update(risk_class="consequential", action_boundary="approval-required",
                      reason_codes=reasons + ["CONSEQUENTIAL_EFFECT", "APPROVAL_REQUIRED"])
    elif issue_class in INELIGIBLE_CLASSES or "substantial-change" in effects:
        result.update(risk_class="substantial", action_boundary="approval-required",
                      reason_codes=reasons + ["APPROVAL_REQUIRED"]
                      + (["PROTECTED_CHANGE"] if issue_class in INELIGIBLE_CLASSES else []))
    elif kind == "edit" and effects == {"local-reversible"} and issue_class in ELIGIBLE_CLASSES:
        result.update(risk_class="routine-reversible",
                      action_boundary="conditional-routine" if reference else "needs-context",
                      reason_codes=reasons + ["ROUTINE_CONDITIONAL"]
                      + ([] if reference else ["MISSING_CONTEXT"]))
    else:
        result["reason_codes"] = reasons + ["UNKNOWN_EFFECT"]
    return result


def _metrics(metrics, paths):
    if (not isinstance(metrics, dict) or set(metrics) != {"raw", "sample_count"}
            or not isinstance(metrics["raw"], dict)
            or type(metrics["sample_count"]) is not int or metrics["sample_count"] < 0):
        return "unavailable", ["METRIC_UNAVAILABLE"]
    raw = dict(metrics["raw"], sample_size=metrics["sample_count"])
    try:
        verdict = evaluate_eligibility(paths, [], raw, default_config())
    except (TypeError, ValueError, OverflowError):
        return "unavailable", ["METRIC_UNAVAILABLE"]
    if verdict.eligible:
        return "eligible-shadow", []
    return "ineligible-shadow", ["METRIC_INELIGIBLE"]


def _reuse(reuse, scope, paths, workflow_schema, resource_schema):
    required = {"previous", "current", "as_of", "source_ids", "evidence_artifacts"}
    optional = {"resource_operation", "destination"}
    invalid = {"reuse_assessment": "invalid", "reason_codes": ["RECEIPT_INVALID"]}
    if not isinstance(reuse, dict) or not required <= set(reuse) or set(reuse) - required - optional:
        return invalid
    current = reuse["current"]
    key = current.get("key") if isinstance(current, dict) else None
    if not isinstance(key, dict):
        return invalid
    if any(key.get(name) != scope[name] for name in ("repository_id", "task_id", "operation_id")):
        return {"reuse_assessment": "invalid", "reason_codes": ["KEY_CHANGED"]}
    if key.get("changed_paths") != paths:
        return {"reuse_assessment": "invalid", "reason_codes": ["KEY_CHANGED"]}
    previous = reuse["previous"]
    has_resources = current.get("resources") or (isinstance(previous, dict) and previous.get("resources"))
    if has_resources and not optional <= set(reuse):
        return {"reuse_assessment": "needs-context", "reason_codes": ["MISSING_CONTEXT"]}
    if workflow_schema is None:
        return {"reuse_assessment": "needs-context", "reason_codes": ["SCHEMA_UNAVAILABLE"]}
    if (not isinstance(reuse["source_ids"], list)
            or any(not _nonempty(s) for s in reuse["source_ids"])
            or not isinstance(reuse["evidence_artifacts"], dict)):
        return invalid
    try:
        return compare_receipts(
            reuse["previous"], current, workflow_schema=workflow_schema,
            resource_schema=resource_schema, as_of=reuse["as_of"],
            source_ids=reuse["source_ids"], evidence_artifacts=reuse["evidence_artifacts"],
            resource_operation=reuse.get("resource_operation", "read"),
            destination=reuse.get("destination", "private"))
    except (TypeError, ValueError, KeyError, RecursionError):
        return invalid


def assess(request, *, workflow_schema=None, resource_schema=None):
    """Assess caller context without verifying permissions or performing operations."""
    try:
        scope, paths, effects, reference = _context(request)
    except (ValueError, TypeError, KeyError):
        result = _unknown()
        if isinstance(request, dict) and "metrics" in request:
            result.update(metric_advice="unavailable")
            result["reason_codes"].append("METRIC_UNAVAILABLE")
        if isinstance(request, dict) and "reuse" in request:
            result.update(reuse_assessment="needs-context")
        result["reason_codes"] = sorted(set(result["reason_codes"]))
        return result
    result = _operation(request, paths, effects, reference)
    if "metrics" in request:
        result["metric_advice"], reasons = _metrics(request["metrics"], paths)
        result["reason_codes"].extend(reasons)
    if "reuse" in request:
        reuse = _reuse(request["reuse"], scope, paths, workflow_schema, resource_schema)
        result["reuse_assessment"] = reuse["reuse_assessment"]
        result["reason_codes"].extend(reuse["reason_codes"])
    result["reason_codes"] = sorted(set(result["reason_codes"]))
    return result


def _schema(name):
    path = Path(__file__).resolve().parents[2] / "config/schemas" / name
    try:
        with path.open("rb") as stream:
            return load_json(stream.read(MAX_BYTES + 1))
    except (OSError, ValueError, RecursionError):
        return None


def main():
    """Bounded stdin and fixed local schemas only; no arbitrary locator reads."""
    try:
        request = load_json(sys.stdin.buffer.read(MAX_BYTES + 1))
        schemas = {}
        if "reuse" in request:
            schemas = {"workflow_schema": _schema("workflow-receipt-v1.schema.json"),
                       "resource_schema": _schema("resource-descriptor-v1.schema.json")}
        result = assess(request, **schemas)
        code = 2 if result["risk_class"] == "unknown" else 0
    except (ValueError, TypeError, RecursionError, UnicodeError):
        result, code = _unknown(), 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
