#!/usr/bin/env python3
"""Compare normalized scheduler snapshots offline (issue #2765).

Usage:
    python scripts/analysis/scheduler_parity_report.py \
        --canonical canonical.json --actual system-cron=system.json \
        --actual gateway=gateway.json --observed-at 2026-10-15T12:00:00Z

The timestamp above is a synthetic example. Each input JSON object has exactly
{"available": bool, "jobs": [{"logical_id": str, "surface": str,
"schedule": str, "runtime": str}]}. Canonical jobs declare intended surfaces;
actual inputs are keyed by surface. A logical_id asserts caller-supplied mapping,
not an identity inferred or authenticated here. Runtime classes are caller-defined
strings. Missing identities, extra fields (including commands), and records in
the wrong actual surface are rejected. Unavailable snapshots must have no jobs.

build_report() is pure; the CLI reads local JSON files and writes JSON to stdout.
An omitted actual surface, a None actual snapshot or a missing actual file is
unknown. An available empty snapshot can establish missing jobs. An unavailable
canonical snapshot makes comparisons unknown. Callers must supply all relevant
surfaces, including empty ones; undisclosed surfaces cannot be discovered here.

Findings are ordered by surface, logical_id, kind and snapshot. Duplicate means
more than one record for the same (logical_id, surface) within a snapshot, per
issue #2765; ambiguous records are never selected for schedule/runtime comparison.
Unique matches compare strings verbatim, with separate schedule/runtime findings.
Mapped actual jobs absent from an available canonical snapshot are unexpected.
"known" describes collection availability, not a clean parity verdict.

Observation time is supplied, never read from a clock. The accepted timestamp
grammar follows RFC 3339 section 5.6 (uppercase T/Z); leap seconds are unsupported.
No freshness, last-run, raw parsing, live collection, installation, migration or
publication is implemented. Those adapters remain follow-up work for issue #2765.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


_JOB_FIELDS = {"logical_id", "surface", "schedule", "runtime"}
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)
# argparse's documented success/error exit convention, not parity verdicts.
_SUCCESS = 0
_INVALID_INPUT = 2


def _nonempty_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")


def _validate_time(observed_at: object) -> None:
    if not isinstance(observed_at, str) or not _TIMESTAMP.fullmatch(observed_at):
        raise ValueError("observed_at must be an explicit RFC 3339 timestamp")
    try:
        datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("observed_at is not a valid calendar timestamp") from None
    # RFC 3339 uses -00:00 for an unknown offset, not a known observation instant.
    if observed_at.endswith("-00:00"):
        raise ValueError("observed_at must have a known timezone offset")


def _index(snapshot: object, *, surface: str | None = None) -> dict:
    if not isinstance(snapshot, dict) or set(snapshot) != {"available", "jobs"}:
        raise ValueError("snapshot requires exactly available and jobs")
    if not isinstance(snapshot["available"], bool):
        raise ValueError("available must be a boolean")
    if not isinstance(snapshot["jobs"], list):
        raise ValueError("jobs must be an array")
    if not snapshot["available"] and snapshot["jobs"]:
        raise ValueError("unavailable snapshot cannot contain jobs")
    indexed = defaultdict(list)
    for record in snapshot["jobs"]:
        if not isinstance(record, dict) or "logical_id" not in record:
            raise ValueError("every job requires a caller-mapped logical_id")
        if set(record) != _JOB_FIELDS:
            raise ValueError("job requires exactly logical_id, surface, schedule and runtime")
        for field in sorted(_JOB_FIELDS):
            _nonempty_string(record[field], field)
        if surface is not None and record["surface"] != surface:
            raise ValueError("job surface differs from actual snapshot surface")
        indexed[(record["logical_id"], record["surface"])].append(record)
    return dict(indexed)


def _finding(kind: str, reason: str, key: tuple, **details) -> dict:
    logical_id, surface = key
    return dict(kind=kind, reason=reason, logical_id=logical_id, surface=surface, **details)


def _duplicates(indexed: dict, source: str) -> list[dict]:
    # Per the identity contract, cardinality greater than one is a duplicate.
    return [
        _finding("duplicate", "repeated_identity_on_surface", key,
                 snapshot=source, count=len(records))
        for key, records in indexed.items() if len(records) > 1
    ]


def build_report(canonical: dict, actuals: dict, *, observed_at: str) -> dict:
    """Return a deterministic report without mutating or collecting inputs.

    actuals maps each caller-declared surface to a normalized snapshot or None.
    Malformed inputs raise ValueError before any report is returned. Duplicates
    are independently observable even if the comparison counterpart is unknown.
    """
    _validate_time(observed_at)
    expected = _index(canonical)
    if not isinstance(actuals, dict):
        raise ValueError("actuals must map surface strings to snapshots")
    indexes = {}
    for surface, snapshot in actuals.items():
        _nonempty_string(surface, "surface")
        indexes[surface] = {} if snapshot is None else _index(snapshot, surface=surface)

    surfaces = sorted({surface for _, surface in expected} | set(actuals))
    findings = _duplicates(expected, "canonical")
    states = []
    for surface in surfaces:
        actual = actuals.get(surface)
        observed = indexes.get(surface, {})
        findings.extend(_duplicates(observed, "actual"))
        reason = None
        if not canonical["available"]:
            reason = "canonical_unavailable"
        elif actual is None:
            reason = "snapshot_missing"
        elif not actual["available"]:
            reason = "snapshot_unavailable"
        if reason is not None:
            states.append(dict(surface=surface, status="unknown", reason=reason))
            continue
        states.append(dict(surface=surface, status="known"))
        intended = {key: rows for key, rows in expected.items() if key[1] == surface}
        for key in intended.keys() | observed.keys():
            wanted, found = intended.get(key, []), observed.get(key, [])
            if not found:
                findings.append(_finding("missing", "absent_from_available_snapshot", key))
            elif not wanted:
                findings.append(_finding("unexpected", "absent_from_canonical_snapshot", key))
            elif len(wanted) == len(found) == 1:
                # The unique-match contract establishes one unambiguous pair.
                want, have = next(iter(wanted)), next(iter(found))
                for field, reason in (("schedule", "schedule_string_differs"),
                                      ("runtime", "runtime_class_differs")):
                    if want[field] != have[field]:
                        findings.append(_finding(
                            f"{field}_mismatch", reason, key,
                            expected=want[field], actual=have[field],
                        ))
    findings.sort(key=lambda row: (
        row["surface"], row["logical_id"], row["kind"], row.get("snapshot", ""),
    ))
    return dict(observed_at=observed_at, canonical_available=canonical["available"],
                surfaces=states, findings=findings)


def report_json(report: dict) -> str:
    """Serialize stable JSON, including object keys, with no generated timestamp."""
    return json.dumps(report, sort_keys=True, ensure_ascii=True, allow_nan=False)


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON numbers are not allowed")


def _load_json(path: str) -> dict:
    with Path(path).open(encoding="utf-8") as source:
        snapshot = json.load(source, object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot JSON must be an object")
    return snapshot


def main(argv: list[str] | None = None) -> int:
    """Read local snapshots; report findings and unknowns without publication."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", required=True, help="normalized canonical JSON file")
    parser.add_argument("--actual", action="append", default=[], metavar="SURFACE=FILE",
                        help="normalized actual JSON file; repeat for each surface")
    parser.add_argument("--observed-at", required=True, help="explicit RFC 3339 observation time")
    args = parser.parse_args(argv)
    try:
        canonical = _load_json(args.canonical)
        actuals = {}
        for item in args.actual:
            surface, separator, path = item.partition("=")
            if not separator or not surface.strip() or not path.strip():
                raise ValueError("actual input must be SURFACE=FILE")
            if surface in actuals:
                raise ValueError("actual surface specified more than once")
            try:
                actuals[surface] = _load_json(path)
            except FileNotFoundError:
                actuals[surface] = None
        result = build_report(canonical, actuals, observed_at=args.observed_at)
    except (OSError, UnicodeError, ValueError):
        # Do not echo supplied paths or raw payloads in diagnostics.
        print("Invalid snapshot input or observation time; no report emitted.", file=sys.stderr)
        return _INVALID_INPUT
    print(report_json(result))
    return _SUCCESS


if __name__ == "__main__":
    sys.exit(main())
