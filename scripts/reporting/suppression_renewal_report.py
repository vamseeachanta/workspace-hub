#!/usr/bin/env python3
"""Build an offline suppression renewal queue and stale-waiver digest.

Contract basis: issue 2191, supplied report-only precedence and explicit-time
requirements. No default clock, horizon, recurrence threshold or policy is used.

Records are JSON-shaped dictionaries with exactly suppression_id, provider,
reason_code, responsible_role, reviewer_role, expiry, last_seen_run,
unresolved_count and renewal_count. Text must be nonempty, trimmed, single-line
UTF-8; reviewer_role may instead be null, denoting missing review. Counts are
nonnegative integers (booleans excluded). Suppression identifiers are unique.
last_seen_run is an opaque reference, never a path to inspect. Unknown fields
are rejected; public responsibility metadata uses responsible_role exclusively.

expiry uses an offset-aware timestamp with calendar date, T, hours, minutes and
seconds, optional microseconds, and Z or a numeric offset. It is normalized to
UTC. as_of is a caller-supplied UTC datetime; due_soon is a nonnegative timedelta.
Zero counts and zero duration follow the supplied contract, not policy defaults.

Independent flags, in precedence order:
* expired: expiry <= as_of (the expiry instant is no longer valid).
* needs-re-review: reviewer_role is null.
* no-longer-observed: unresolved_count == zero.
* due-soon: zero < expiry - as_of <= due_soon (inclusive horizon).
The first applicable flag determines state; no flags means current. An expired
row retains missing-review and zero-observed flags, but is never due-soon.

queue contains every record, including current records, sorted by state priority,
expiry instant, provider and suppression_id. digest contains total, state_counts,
flag_counts and groups. Groups are joint provider/reviewer_role/renewal_count
cohorts, sorted lexically by provider and reviewer (null first), then numerically
by renewal_count. Counts omit absent states/flags; overlapping flag counts need
not sum to row counts. Recurrence is the exact renewal_count, without bucketing.

build_report and render_report perform no I/O or mutation. The CLI reads only
an explicit JSON array from standard input, emits JSON to standard output, and
requires --as-of and --due-soon-seconds (whole nonnegative seconds). It never
renews suppressions, invokes gates, publishes or discovers live inventories.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any


_STATES = ("expired", "needs-re-review", "no-longer-observed", "due-soon", "current")
_TEXT_FIELDS = (
    "suppression_id", "provider", "reason_code", "responsible_role", "last_seen_run",
)
_FIELDS = {*_TEXT_FIELDS, "reviewer_role", "expiry", "unresolved_count", "renewal_count"}
# Calendar/time field widths and microsecond precision express the input grammar
# documented above; they do not encode a suppression policy threshold.
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])\Z"
)


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValueError("invalid timestamp")
    try:
        # The grammar rejects overflowing offset fields before normalization.
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise ValueError("invalid timestamp") from error


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_text(value: Any) -> None:
    if (not isinstance(value, str) or not value or value != value.strip()
            or any(not character.isprintable() for character in value)):
        raise ValueError("invalid text field")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ValueError("invalid text field") from error


def _counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Unit increments are the hand-counted row/flag occurrences, not thresholds.
    return {
        "state_counts": dict(sorted(Counter(row["state"] for row in rows).items())),
        "flag_counts": dict(sorted(Counter(flag for row in rows for flag in row["flags"]).items())),
    }


def build_report(records: list[dict[str, Any]], *, as_of: datetime,
                 due_soon: timedelta) -> dict[str, Any]:
    """Validate explicit records and return a detached JSON-compatible report.

    Malformed records or policy arguments raise ValueError without returning a
    partial report. Neither caller data nor suppression renewal state is changed.
    """
    if (not isinstance(as_of, datetime) or as_of.tzinfo is None
            or as_of.utcoffset() != timedelta(0)):
        raise ValueError("as_of must be an explicit UTC datetime")
    if not isinstance(due_soon, timedelta) or due_soon < timedelta(0):
        raise ValueError("due_soon must be an explicit nonnegative timedelta")
    if not isinstance(records, list):
        raise ValueError("records must be an array")

    ordered = []
    identifiers = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != _FIELDS:
            raise ValueError("invalid record fields")
        for field in _TEXT_FIELDS:
            _validate_text(record[field])
        if record["reviewer_role"] is not None:
            _validate_text(record["reviewer_role"])
        for field in ("unresolved_count", "renewal_count"):
            if type(record[field]) is not int or record[field] < 0:
                raise ValueError("counts must be nonnegative integers")
        identifier = record["suppression_id"]
        if identifier in identifiers:
            raise ValueError("duplicate suppression identifier")
        identifiers.add(identifier)
        expiry = _timestamp(record["expiry"])
        remaining = expiry - as_of
        conditions = (
            expiry <= as_of,
            record["reviewer_role"] is None,
            record["unresolved_count"] == 0,
            timedelta(0) < remaining <= due_soon,
        )
        flags = [state for state, applies in zip(_STATES, conditions) if applies]
        state = next(iter(flags), "current")
        row = {**record, "expiry": _utc_text(expiry), "state": state, "flags": flags}
        ordered.append((expiry, row))

    ordered.sort(key=lambda item: (
        _STATES.index(item[1]["state"]), item[0],
        item[1]["provider"], item[1]["suppression_id"],
    ))
    queue = [row for _, row in ordered]
    cohorts: dict[tuple[str, str | None, int], list[dict[str, Any]]] = {}
    for row in queue:
        key = (row["provider"], row["reviewer_role"], row["renewal_count"])
        cohorts.setdefault(key, []).append(row)
    groups = []
    for key in sorted(cohorts, key=lambda key: (key[0], key[1] or "", key[2])):
        provider, reviewer, renewals = key
        groups.append({
            "provider": provider, "reviewer_role": reviewer, "renewal_count": renewals,
            "count": len(cohorts[key]), **_counts(cohorts[key]),
        })
    return {
        "as_of": _utc_text(as_of), "due_soon_seconds": due_soon.total_seconds(),
        "queue": queue,
        "digest": {"total": len(queue), **_counts(queue), "groups": groups},
    }


def render_report(records: list[dict[str, Any]], *, as_of: datetime,
                  due_soon: timedelta) -> str:
    """Return deterministic JSON text without reading or writing external state."""
    return json.dumps(build_report(records, as_of=as_of, due_soon=due_soon),
                      sort_keys=True, ensure_ascii=False, allow_nan=False)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("non-finite JSON value")


class _PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's command-usage status, with no rejected input echoed.
        self.exit(2, "invalid report input or arguments\n")


def main(argv: list[str] | None = None) -> int:
    """Read an explicit stdin array and emit JSON; no inventory discovery."""
    parser = _PrivateParser(description="Offline suppression renewal report")
    parser.add_argument("--as-of", required=True, help="UTC timestamp")
    parser.add_argument("--due-soon-seconds", required=True, type=int,
                        help="Explicit nonnegative horizon in whole seconds")
    args = parser.parse_args(argv)
    try:
        as_of = _timestamp(args.as_of)
        # The CLI, like the API, requires an explicitly UTC reference instant.
        if not (args.as_of.endswith("Z") or args.as_of.endswith("+00:00")):
            raise ValueError("as_of must be UTC")
        horizon = timedelta(seconds=args.due_soon_seconds)
        records = json.loads(sys.stdin.read(), object_pairs_hook=_unique_pairs,
                             parse_constant=_invalid_constant)
        output = render_report(records, as_of=as_of, due_soon=horizon)
    except (ValueError, OverflowError, OSError, RecursionError):
        parser.error("invalid report input")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
