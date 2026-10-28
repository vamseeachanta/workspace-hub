"""Offline content composition; no solver invocation or qualification authority.

Contract source: issue #3849 (2026), Reproduced verification gaps and Proposed
follow-on. No engineering coefficients or acceptance limits are supplied here.
Domain extraction, snapshot completeness and provenance need independent review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, DecimalException
from pathlib import Path

PASS = "PASS"
FAIL = "FAIL"
NOT_EVALUATED = "NOT_EVALUATED"


def _finite(value):
    # Retain the supported finite float magnitude range, without rounding decimals.
    return type(value) in (int, float, Decimal) and (
        type(value) is int or math.isfinite(value))


def _validate_json(value):
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("JSON keys must be strings")
        for item in value.values():
            _validate_json(item)
    elif isinstance(value, list):
        for item in value:
            _validate_json(item)
    elif value is not None and type(value) not in (str, bool, int, float, Decimal):
        raise ValueError("Unsupported JSON value")
    elif type(value) in (float, Decimal) and not _finite(value):
        raise ValueError("Non-finite JSON number")


def _pairs(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("Duplicate JSON key")
        record[key] = value
    return record


def read_record(raw):
    """Reject duplicates and non-finite values before evidence can lose meaning."""
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_float=Decimal)
    except DecimalException:
        raise ValueError("Invalid decimal number") from None
    if not isinstance(value, dict):
        raise TypeError("Expected JSON object")
    _validate_json(value)
    return value


def _canonical(value):
    _validate_json(value)
    if isinstance(value, dict):
        return ("object", tuple((key, _canonical(item))
                                for key, item in sorted(value.items())))
    if isinstance(value, list):
        return ("array", tuple(_canonical(item) for item in value))
    if type(value) in (float, Decimal):
        # Direct API floats have already lost their original JSON token; compare
        # their round-trip decimal spelling with parsed decimal evidence.
        return ("decimal", Decimal(str(value)))
    return (type(value).__name__, value)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _mapping(value):
    return isinstance(value, dict) and bool(value)


def _digest(value):
    # SHA-256 hexadecimal representation: FIPS PUB 180-4 (2015), section 6.2.
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value)


def _binding(requirements, source, evidence_bytes, evidence):
    fields = ("input_sha256", "evidence_sha256", "evidence_kind")
    if any(field not in requirements for field in fields):
        return NOT_EVALUATED
    if any(field not in evidence for field in ("input_sha256", "evidence_kind")):
        return NOT_EVALUATED
    input_digest = hashlib.sha256(source).hexdigest()
    matches = (
        _digest(requirements["input_sha256"])
        and _digest(requirements["evidence_sha256"])
        and requirements["input_sha256"] == evidence["input_sha256"] == input_digest
        and requirements["evidence_sha256"] == hashlib.sha256(evidence_bytes).hexdigest()
        and requirements["evidence_kind"] in ("synthetic", "native")
        and requirements["evidence_kind"] == evidence["evidence_kind"]
    )
    return PASS if matches else FAIL


def _domain(requirements, evidence):
    # Exact declared-domain comparison, not a bounds/resultant surrogate (#3849).
    if "domain" not in requirements or "domain" not in evidence:
        return NOT_EVALUATED
    expected, observed = requirements["domain"], evidence["domain"]
    if not _mapping(expected) or not _mapping(observed):
        return FAIL
    return PASS if _canonical(expected) == _canonical(observed) else FAIL


def _event(value):
    # Nonnegative event ordinals are protocol ordering, not a physical limit.
    return type(value) is int and value >= 0


def _settings(requirements, evidence):
    expected = requirements.get("settings")
    history = evidence.get("settings_history")
    result = evidence.get("result")
    if expected is None or history is None or result is None:
        return NOT_EVALUATED
    if not _mapping(expected) or not isinstance(history, list) or not _mapping(result):
        return FAIL
    if not history:
        return NOT_EVALUATED
    if "event" not in result or "settings_event" not in result:
        return NOT_EVALUATED
    if not _event(result["event"]) or not _event(result["settings_event"]):
        return FAIL
    previous = -1  # Sentinel preceding the first permitted event ordinal.
    applicable = None
    for snapshot in history:
        if not isinstance(snapshot, dict):
            return FAIL
        if not all(key in snapshot for key in ("event", "source", "values")):
            return NOT_EVALUATED
        event = snapshot["event"]
        if (not _event(event) or event <= previous or not _text(snapshot["source"])
                or not _mapping(snapshot["values"])):
            return FAIL
        previous = event
        if event == result["event"]:
            return FAIL
        if event < result["event"]:
            applicable = snapshot
    if applicable is None:
        return NOT_EVALUATED
    # Each snapshot is complete, not a delta; defaults never fill absent fields.
    matches = (result["settings_event"] == applicable["event"]
               and _canonical(expected) == _canonical(applicable["values"]))
    return PASS if matches else FAIL


def _criterion(requirements, evidence):
    criterion, result = requirements.get("criterion"), evidence.get("result")
    if criterion is None or result is None:
        return NOT_EVALUATED
    if not isinstance(criterion, dict) or not isinstance(result, dict):
        return FAIL
    labels = ("result_id", "quantity", "unit")
    if (not all(key in criterion for key in (*labels, "source", "minimum", "maximum"))
            or not all(key in result for key in (*labels, "value"))):
        return NOT_EVALUATED
    if (not _text(criterion["source"])
            or not all(_text(criterion[key]) and criterion[key] == result[key]
                       for key in labels)):
        return FAIL
    lower, upper, value = criterion["minimum"], criterion["maximum"], result["value"]
    if not all(_finite(number) for number in (lower, upper, value)):
        return FAIL
    lower, upper, value = (Decimal(str(number)) for number in (lower, upper, value))
    if lower > upper:
        return FAIL
    # Inclusive interval is caller-specified; no solver/standard limit is assumed.
    return PASS if lower <= value <= upper else FAIL


def compose(requirements, source, evidence_bytes):
    """Compare frozen declared evidence; never infer whole-model readiness.

    Requirements must be independently reviewed. Hashes establish byte agreement,
    not authenticity, execution, completeness of extraction or engineering truth.
    All sub-checks run, even when source binding or another criterion fails.
    """
    if not isinstance(requirements, dict):
        raise TypeError("Expected requirements object")
    _validate_json(requirements)
    evidence = read_record(evidence_bytes)
    checks = {
        "binding": _binding(requirements, source, evidence_bytes, evidence),
        "domain": _domain(requirements, evidence),
        "settings": _settings(requirements, evidence),
        "criterion": _criterion(requirements, evidence),
    }
    # Conjunction with explicit unknowns: a failure dominates incomplete evidence.
    status = FAIL if FAIL in checks.values() else (
        NOT_EVALUATED if NOT_EVALUATED in checks.values() else PASS)
    return {
        "content_status": status,
        "checks": checks,
        "evidence_kind": (evidence["evidence_kind"]
                          if evidence.get("evidence_kind") in ("synthetic", "native")
                          else "unknown"),
        "whole_model_readiness": NOT_EVALUATED,
        "provenance": "independently_unverified",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirements", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        report = compose(read_record(args.requirements.read_bytes()),
                         args.input.read_bytes(), args.evidence.read_bytes())
    except (OSError, ValueError, TypeError, RecursionError):
        # Do not echo payloads, paths or parser exception details into public logs.
        parser.exit(2, "Invalid or unreadable composition record\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["content_status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
