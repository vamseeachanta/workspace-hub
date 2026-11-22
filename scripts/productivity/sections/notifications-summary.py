#!/usr/bin/env python3
"""Summarize an explicitly supplied, normalized notification JSONL file.

Usage: python scripts/productivity/sections/notifications-summary.py INPUT

Issue #3655 defines this aggregate-only consumer. Each object requires a nonblank
string event_key, severity (info/warning/error/critical), and boolean acknowledged.
The last valid row for a key wins in file order, including acknowledgement and
severity changes. Invalid later rows do not overwrite valid state. Optional source
is a string, reduced to the fixed categories declared in scripts/notify.sh and
scripts/email/state/notifications.py; all other values become other. Extra fields
are ignored and never printed. Duplicate JSON fields and non-finite values are
malformed, as are blank lines and invalid UTF-8 lines.

Counts start at zero and increment once per qualifying row or unique unread key;
these are arithmetic counts, with no policy thresholds. Exit zero means complete
input, one means missing/unreadable/partial input; argparse retains its standard
usage-error status. These statuses are local CLI conventions, not severity policy.
The current writers do not provide this normalized key/severity/acknowledgement
contract. No writer adaptation, daily-summary wiring, delivery or acknowledgement
is performed here. Input order is authoritative; timestamps are not interpreted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SEVERITIES = ("info", "warning", "error", "critical")
CATEGORIES = ("cron", "ci", "benchmark", "email", "other")


class NeutralParser(argparse.ArgumentParser):
    """Do not echo arbitrary arguments or invocation paths in diagnostics."""

    def error(self, message):
        self.exit(2, "error: expected one input file argument\n")


def _object(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("duplicate field")
        record[key] = value
    return record


def _nonfinite(value):
    raise ValueError("non-finite value")


def _parse(line: bytes):
    record = json.loads(
        line.decode("utf-8"), object_pairs_hook=_object, parse_constant=_nonfinite
    )
    if not isinstance(record, dict):
        raise ValueError("expected object")
    key = record.get("event_key")
    severity = record.get("severity")
    acknowledged = record.get("acknowledged")
    source = record.get("source", "other")
    if (
        not isinstance(key, str)
        or not key.strip()
        or severity not in SEVERITIES
        or type(acknowledged) is not bool
        or not isinstance(source, str)
    ):
        raise ValueError("invalid event")
    category = source if source in CATEGORIES else "other"
    return key, (severity, acknowledged, category)


def summarize(path: Path) -> dict:
    """Read one file without writes; return only fixed labels and counts."""
    summary = {
        "input_status": "ok",
        "unique_events": 0,
        "duplicate_records": 0,
        "malformed_records": 0,
        "unread_total": 0,
        "unread_by_severity": dict.fromkeys(SEVERITIES, 0),
        "unread_by_category": dict.fromkeys(CATEGORIES, 0),
    }
    events = {}
    try:
        with path.open("rb") as handle:
            for line in handle:
                try:
                    key, event = _parse(line)
                except (ValueError, RecursionError):
                    summary["malformed_records"] += 1
                    continue
                if key in events:
                    summary["duplicate_records"] += 1
                events[key] = event
    except FileNotFoundError:
        summary["input_status"] = "missing"
    except (OSError, ValueError):
        summary["input_status"] = "unreadable"
    if summary["input_status"] == "ok" and summary["malformed_records"]:
        summary["input_status"] = "partial"
    summary["unique_events"] = len(events)
    for severity, acknowledged, category in events.values():
        if not acknowledged:
            summary["unread_total"] += 1
            summary["unread_by_severity"][severity] += 1
            summary["unread_by_category"][category] += 1
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = NeutralParser(
        prog="notifications-summary.py",
        description="Print aggregate unread counts from normalized local JSONL.",
    )
    parser.add_argument("input", metavar="INPUT", help="Input JSONL file (read only)")
    args = parser.parse_args(argv)
    summary = summarize(Path(args.input))
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["input_status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
