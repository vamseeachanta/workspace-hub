#!/usr/bin/env python3
"""Offline clock-evidence replay; PASS is neither admission nor a reservation.

Clock semantics: Python 3.13 time documentation, time.monotonic_ns/time.time_ns
and get_clock_info; docs/monitoring/clock-domain-audit.html defines the contract.
No conversions between clock identities or resolutions are inferred.
"""

from __future__ import annotations

import copy
import json
import sys


class EvidenceGap(ValueError):
    """Evidence cannot establish the proposed comparison."""


def _integer(value, name, *, positive=False):
    # Zero is the arithmetic origin, not a default operational threshold.
    if type(value) is not int or value < 0 or (positive and value == 0):
        raise EvidenceGap(f"{name}: nonnegative integer required")
    return value


def _reading(value):
    if not isinstance(value, dict):
        raise EvidenceGap("clock reading required")
    tick = _integer(value.get("value_ns"), "value_ns")
    resolution = _integer(value.get("resolution_ns"), "resolution_ns", positive=True)
    if value.get("domain") not in ("wall", "monotonic"):
        raise EvidenceGap("explicit wall or monotonic domain required")
    if not isinstance(value.get("clock_id"), str) or not value["clock_id"].strip():
        raise EvidenceGap("clock origin identity required")
    return tick, (value["domain"], value["clock_id"], resolution)


def _limits(packet):
    criteria = packet.get("criteria")
    if not isinstance(criteria, dict):
        raise EvidenceGap("explicit criteria required")
    low, high, max_age = (
        _integer(criteria.get(key), key)
        for key in ("min_duration_ns", "max_duration_ns", "max_age_ns")
    )
    if low > high:
        raise EvidenceGap("duration limits are reversed")
    return low, high, max_age


def _sample(sample, wall_identity, duration_identity):
    if not isinstance(sample, dict):
        raise EvidenceGap("sample object required")
    start, identity = _reading(sample.get("start"))
    end, end_identity = _reading(sample.get("end"))
    interval, interval_identity = _reading(sample.get("interval"))
    observed, observed_identity = _reading(sample.get("observed_at"))
    if identity != end_identity or identity != interval_identity:
        raise EvidenceGap("duration clock domain, origin or resolution mismatch")
    if duration_identity is not None and identity != duration_identity:
        raise EvidenceGap("continuity clock domain, origin or resolution mismatch")
    if observed_identity != wall_identity:
        raise EvidenceGap("freshness clock domain, origin or resolution mismatch")
    return start, end, interval, observed, identity


def _evaluate(packet):
    low, high, max_age = _limits(packet)
    now, wall_identity = _reading(packet.get("now"))
    if wall_identity[0] != "wall":
        raise EvidenceGap("freshness requires wall-clock now")
    samples = packet.get("samples")
    if not isinstance(samples, list) or not samples:
        raise EvidenceGap("nonempty samples required")
    durations, violations = [], []
    previous_end = previous_wall = duration_identity = None
    for sample in samples:
        start, end, interval, observed, duration_identity = _sample(
            sample, wall_identity, duration_identity
        )
        duration = end - start
        durations.append(duration)
        if duration < 0 or (previous_end is not None and start < previous_end):
            violations.append("backward or overlapping duration window")
        if duration != interval:
            violations.append("interval differs from endpoint subtraction")
        if not low <= duration <= high:
            violations.append("duration outside supplied inclusive limits")
        if previous_wall is not None and observed < previous_wall:
            violations.append("wall observations moved backward")
        if now < observed:
            violations.append("future wall observation")
        previous_end, previous_wall = end, observed
    age = now - previous_wall
    if age > max_age:
        violations.append("latest wall observation is stale")
    return {
        "replay_status": "FAIL" if violations else "PASS",
        "reasons": violations,
        "durations_ns": durations,
        "age_ns": age,
    }


def replay(packet):
    """Retain original evidence; absent conversions/criteria are NOT_EVALUATED.

    Only the latest observation is subject to freshness, as declared in the
    replay contract. All observations must be ordered and no later than now.
    """
    evidence = copy.deepcopy(packet)
    try:
        if not isinstance(packet, dict):
            raise EvidenceGap("packet object required")
        result = _evaluate(packet)
    except EvidenceGap as exc:
        result = {"replay_status": "NOT_EVALUATED", "reasons": [str(exc)]}
    return {**result, "evidence": evidence}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def main():
    """Read one JSON packet on stdin; emit replay plus unchanged parsed evidence."""
    try:
        packet = json.load(
            sys.stdin, object_pairs_hook=_unique_object, parse_constant=_reject_constant
        )
        result = replay(packet)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if result["replay_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
