#!/usr/bin/env python3
"""Compare supplied metric snapshots without collecting or regenerating reports.

Scope: issue #2122, deltas and new-regression sections only. Existing declarations
in scripts/analysis/weekly-trends.py:get_week_key and compute_drift_metrics supply
weekly grouping and violations-per-day context, not acceptance thresholds. No
policy numbers are inferred from them or from the issue.

Each snapshot maps metric IDs to {definition, unit, value}; value may be null.
The previous snapshot itself may be null for a first observation. Policies map
IDs to {definition, unit, direction, threshold}. All observed IDs require a policy;
policy-only IDs are reported as missing. Definition and unit strings must match
exactly across observations and policy; no unit conversion is attempted.

Direction is 'higher' or 'lower' for the preferred value. Threshold is an inclusive
acceptance limit in the declared unit: higher accepts value >= threshold, lower
accepts value <= threshold. A new regression is a known acceptable predecessor
followed by an unacceptable current value. An already unacceptable predecessor
does not produce a new regression. Trend independently describes current minus
previous. Missing or incompatible observations yield unknown comparisons (JSON
null), never an invented zero. The arithmetic zero below is the additive identity,
not a policy threshold. Decimal spellings of finite JSON numbers determine deltas.

compute_deltas is pure; canonical_json returns compact, sorted-key JSON with metric
and regression lists sorted by ID. CLI: previous.json current.json policies.json;
output goes only to stdout. Callers select and order periods, supply qualified
definitions and thresholds, and handle persistence. No live-data coverage, colour
bands, percentage changes, chronology checks or publication entry point is implied.
"""

import argparse
import json
import math
from collections.abc import Mapping
from fractions import Fraction
from pathlib import Path


def _mapping(value, label):
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    for key in value:
        _text(key, f"{label} metric ID")
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return Fraction(str(value))


def _validate_record(record, label, *, is_policy=False):
    _mapping(record, label)
    for field in ("definition", "unit"):
        _text(record.get(field), f"{label} {field}")
    if is_policy:
        if record.get("direction") not in ("higher", "lower"):
            raise ValueError(f"{label} direction must be higher or lower")
        _number(record.get("threshold"), f"{label} threshold")
    else:
        if "value" not in record:
            raise ValueError(f"{label} value is required; use null for missing")
        if record["value"] is not None:
            _number(record["value"], f"{label} value")


def _regressed(record, policy):
    if record is None or record["value"] is None:
        return None
    value = _number(record["value"], "value")
    threshold = _number(policy["threshold"], "threshold")
    return value < threshold if policy["direction"] == "higher" else value > threshold


def _json_number(value):
    if value.denominator == 1:  # Integral fractions have denominator one.
        return value.numerator
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("delta is outside the finite JSON number range") from exc
    if not math.isfinite(result) or (result == 0 and value != 0):
        raise ValueError("delta is outside the finite JSON number range")
    return result


def compute_deltas(previous, current, policies):
    """Return deterministic deltas and newly crossed acceptance limits.

    Invalid structure or nonfinite numbers raise ValueError. Legitimate missing
    observations and incompatible metadata produce explicit unknown rows instead.
    Inputs are never mutated. See the module contract for the policy semantics.
    """
    previous = {} if previous is None else _mapping(previous, "previous")
    current = _mapping(current, "current")
    policies = _mapping(policies, "policies")
    observed = set(previous) | set(current)
    if observed - policies.keys():
        raise ValueError("each observed metric requires an explicit policy")
    for metric in sorted(policies):
        _validate_record(policies[metric], "policy", is_policy=True)
    for snapshot in (previous, current):
        for metric in sorted(snapshot):
            _validate_record(snapshot[metric], "observation")

    rows = []
    new_regressions = []
    for metric in sorted(set(policies) | observed):
        policy = policies[metric]
        before, after = previous.get(metric), current.get(metric)
        row = {
            "metric": metric, **{key: policy[key] for key in (
                "definition", "unit", "direction", "threshold",
            )},
            "delta": None, "trend": "unknown", "reason": None,
            "previous_regression": None, "current_regression": None,
            "new_regression": None,
        }
        records = [record for record in (before, after) if record is not None]
        for field, reason in (("definition", "incompatible_definitions"),
                              ("unit", "incompatible_units")):
            if any(record[field] != policy[field] for record in records):
                row["reason"] = reason
                break
        if row["reason"] is not None:
            rows.append(row)
            continue

        row["previous_regression"] = _regressed(before, policy)
        row["current_regression"] = _regressed(after, policy)
        missing_previous = before is None or before["value"] is None
        missing_current = after is None or after["value"] is None
        if missing_previous or missing_current:
            row["reason"] = (
                "missing_previous_and_current" if missing_previous and missing_current
                else "missing_previous" if missing_previous else "missing_current"
            )
        else:
            delta = _number(after["value"], "current") - _number(before["value"], "previous")
            row["delta"] = _json_number(delta)
            if delta == 0:
                row["trend"] = "unchanged"
            else:
                improving = (delta > 0) == (policy["direction"] == "higher")
                row["trend"] = "improving" if improving else "regressing"
            row["new_regression"] = (
                row["previous_regression"] is False and row["current_regression"] is True
            )
            if row["new_regression"]:
                new_regressions.append(metric)
        rows.append(row)
    return {"metrics": rows, "new_regressions": new_regressions}


def canonical_json(result):
    """Serialize a compute_deltas result; no timestamp or platform state is added."""
    return json.dumps(result, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("nonfinite JSON number")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("policies", type=Path)
    args = parser.parse_args(argv)
    try:
        inputs = [json.loads(path.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
                  for path in (args.previous, args.current, args.policies)]
        output = canonical_json(compute_deltas(*inputs))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Invalid scorecard input ({type(exc).__name__}).\n")
    print(output)


if __name__ == "__main__":
    main()
