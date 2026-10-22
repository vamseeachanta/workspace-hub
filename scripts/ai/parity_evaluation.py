#!/usr/bin/env python3
"""Qualify behavioral parity evidence without implicit acceptance thresholds.

Definitions extend scripts/ai/parity_metrics.py (D1 and D2, issue 3061):
T = sum(output tokens) / sum(model turns); A = sum(AskUserQuestion) / sessions.
Criteria are caller-supplied policy inputs, not published engineering constants.
This evaluates reported counts, not transcript completeness or output quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

CRITERIA_KEYS = {
    "reference", "minimum_sessions", "verbosity_multiplier", "clarification_delta",
}


def validate_criteria(criteria):
    """Require a named criterion and explicit limits; provide no defaults."""
    if not isinstance(criteria, dict) or set(criteria) != CRITERIA_KEYS:
        raise ValueError("criteria must contain exactly the documented fields")
    if not isinstance(criteria["reference"], str) or not criteria["reference"].strip():
        raise ValueError("criteria reference must be nonempty")
    minimum = criteria["minimum_sessions"]
    if type(minimum) is not int or minimum <= 0:
        raise ValueError("minimum_sessions must be a positive integer")
    for key in ("verbosity_multiplier", "clarification_delta"):
        value = criteria[key]
        if type(value) not in (int, float):
            raise ValueError(f"{key} must be numeric")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{key} must be finite")
        if value < 0 or (key == "verbosity_multiplier" and value == 0):
            raise ValueError(f"{key} is outside its mathematical domain")


def _count_map(record, key):
    counts = record.get(key)
    if not isinstance(counts, dict):
        raise TypeError(f"{key} must be a count mapping")
    for name, count in counts.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("count labels must be nonempty strings")
        if type(count) is not int or count < 0:
            raise ValueError("counts must be nonnegative integers")
    return counts


def _cohort(digests, model):
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be nonempty")
    result = {"sessions": 0, "turns": 0, "tokens": 0, "asks": 0, "mixed": False}
    for record in digests:
        if not isinstance(record, dict):
            raise TypeError("each digest must be an object")
        turns = _count_map(record, "turns_by_model")
        tokens = _count_map(record, "out_tokens_by_model")
        tools = _count_map(record, "tool_histogram")
        if any(value and not turns.get(name, 0) for name, value in tokens.items()):
            raise ValueError("output tokens require observed model turns")
        if not turns.get(model, 0):
            continue
        if model not in tokens:
            raise ValueError("selected model output-token evidence is missing")
        result["sessions"] += 1
        result["turns"] += turns[model]
        result["tokens"] += tokens[model]
        result["asks"] += tools.get("AskUserQuestion", 0)
        result["mixed"] |= sum(count > 0 for count in turns.values()) > 1
    return result


def _not_evaluated(reason):
    return {"status": "NOT_EVALUATED", "reason": reason}


def _compare(current, baseline, limit):
    # Compare exact fractions before presentation rounding. Decimal input limits
    # are interpreted by their decimal string, avoiding binary boundary drift.
    status = "REGRESSION" if current > limit else "WITHIN_LIMITS"
    try:
        # Presentation is to three decimal places; these values do not drive status.
        values = {key: round(float(value), 3) for key, value in
                  (("current", current), ("baseline", baseline), ("limit", limit))}
    except OverflowError as exc:
        raise ValueError("metric exceeds supported JSON numeric range") from exc
    return {"status": status, **values}


def evaluate_parity(current_digests, baseline_digests, model, baseline_model, criteria):
    """Return per-metric qualification; partial evidence never implies parity.

    Equality meets the supplied upper limit. A regression remains visible even
    if another metric cannot be evaluated. Session tool totals are attributable
    only when every included session has a single active model.
    """
    validate_criteria(criteria)
    current = _cohort(current_digests, model)
    baseline = _cohort(baseline_digests, baseline_model)
    metrics = {}
    enough = all(c["sessions"] >= criteria["minimum_sessions"] for c in (current, baseline))
    if not enough:
        reason = "both cohorts must meet minimum_sessions"
        metrics = {name: _not_evaluated(reason) for name in
                   ("tokens_per_turn", "askuser_per_session")}
    else:
        if baseline["tokens"] == 0:
            metrics["tokens_per_turn"] = _not_evaluated("reference token rate is zero")
        else:
            cur = Fraction(current["tokens"], current["turns"])
            base = Fraction(baseline["tokens"], baseline["turns"])
            limit = base * Fraction(str(criteria["verbosity_multiplier"]))
            metrics["tokens_per_turn"] = _compare(cur, base, limit)
        if current["mixed"] or baseline["mixed"]:
            metrics["askuser_per_session"] = _not_evaluated(
                "session tool counts cannot be attributed across active models")
        else:
            cur = Fraction(current["asks"], current["sessions"])
            base = Fraction(baseline["asks"], baseline["sessions"])
            limit = base + Fraction(str(criteria["clarification_delta"]))
            metrics["askuser_per_session"] = _compare(cur, base, limit)
    states = {metric["status"] for metric in metrics.values()}
    status = ("REGRESSION" if "REGRESSION" in states else
              "NOT_EVALUATED" if "NOT_EVALUATED" in states else "WITHIN_LIMITS")
    return {"status": status, "criteria": dict(criteria), "metrics": metrics,
            "samples": {"current": current["sessions"], "baseline": baseline["sessions"]}}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("non-finite JSON constant")


def read_object(path, evidence=None):
    """Read strict JSON; errors expose no input payloads or filesystem paths."""
    try:
        payload = Path(path).read_bytes()
        result = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=_reject_constant)
    except (OSError, ValueError, RecursionError) as exc:
        raise ValueError("input is unreadable or invalid JSON") from exc
    if not isinstance(result, dict):
        raise TypeError("input must be a JSON object")
    if evidence is not None:
        evidence.append(hashlib.sha256(payload).hexdigest())
    return result


def load_cohort(directory, evidence=None):
    """Load every immediate JSON digest; never skip a malformed input."""
    path = Path(directory)
    if not path.is_dir():
        raise ValueError("cohort directory is unavailable")
    return [read_object(item, evidence) for item in sorted(path.glob("*.json"))]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current_dir")
    parser.add_argument("baseline_dir")
    parser.add_argument("--model", required=True)
    parser.add_argument("--baseline-model", required=True)
    parser.add_argument("--criteria", required=True)
    args = parser.parse_args(argv)
    evidence = {"current": [], "baseline": [], "criteria": []}
    try:
        report = evaluate_parity(
            load_cohort(args.current_dir, evidence["current"]),
            load_cohort(args.baseline_dir, evidence["baseline"]),
            args.model, args.baseline_model, read_object(args.criteria, evidence["criteria"]),
        )
        report["models"] = {"current": args.model, "baseline": args.baseline_model}
        report["evidence_sha256"] = evidence
    except (ValueError, TypeError) as exc:
        report = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(report, indent=2, allow_nan=False))
    # Process convention: success, detected regression, unavailable/invalid evidence.
    return {"WITHIN_LIMITS": 0, "REGRESSION": 1}.get(report["status"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
