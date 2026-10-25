"""Validate dashboard JSON and prepare a daily alert without publishing it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime

# Source: issue #3596, "Thresholds" table (2026), also implemented in
# compliance-cron.sh at the time of the alert. The pass threshold is supplied
# by the dashboard so a configured threshold cannot disagree with its verdict.
CRITICAL_BELOW = 30
HIGH_BELOW = 50
PERCENT = 100  # Percentage definition; dashboard guide, calculation method (2026).


def validate_report(report: dict, run_date: str) -> None:
    """Reject inconsistent counters, stale data and unsupported report formats."""
    if not isinstance(report, dict):
        raise TypeError("dashboard report must be an object")
    integer_fields = (
        "schema_version", "window_hours", "total_commits", "skipped", "reviewable",
        "reviewed", "unreviewed", "compliance_rate", "threshold",
    )
    for field in integer_fields:
        if type(report.get(field)) is not int or report[field] < 0:
            raise ValueError(f"invalid dashboard field: {field}")
    if report["schema_version"] != 1 or not report["window_hours"]:
        raise ValueError("unsupported schema or empty time window")
    if report["threshold"] > PERCENT:
        raise ValueError("threshold exceeds percentage range")
    if report["total_commits"] != report["skipped"] + report["reviewable"]:
        raise ValueError("total does not equal skipped plus reviewable")
    if report["reviewable"] != report["reviewed"] + report["unreviewed"]:
        raise ValueError("reviewable does not equal reviewed plus unreviewed")
    reviewable = report["reviewable"]
    rate = report["reviewed"] * PERCENT // reviewable if reviewable else 0
    if report["compliance_rate"] != rate:
        raise ValueError("compliance rate disagrees with counters")
    verdict = "FAIL" if reviewable and rate < report["threshold"] else "PASS"
    if report.get("verdict") != verdict:
        raise ValueError("dashboard verdict disagrees with counters and threshold")
    try:
        timestamp = datetime.fromisoformat(report["timestamp"])
        current_date = date.fromisoformat(run_date)
    except (KeyError, AttributeError, TypeError, ValueError):
        raise ValueError("invalid dashboard timestamp or run date") from None
    if timestamp.tzinfo is None or timestamp.date() != current_date:
        raise ValueError("dashboard timestamp is stale or has no timezone")
    backlog = report.get("unreviewed_commits")
    if not isinstance(backlog, list) or len(backlog) != report["unreviewed"]:
        raise ValueError("backlog length disagrees with unreviewed count")
    hashes = set()
    for entry in backlog:
        if not isinstance(entry, dict):
            raise TypeError("backlog entry must be an object")
        commit = entry.get("hash")
        subject = entry.get("subject")
        # Source: Git 2.55.0, hash-function-transition, "Object names":
        # https://git-scm.com/docs/hash-function-transition (accessed 2026-10-22).
        if not isinstance(commit, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
            raise ValueError("invalid backlog hash")
        if commit in hashes:
            raise ValueError("duplicate backlog hash")
        hashes.add(commit)
        if not isinstance(subject, str) or not subject.strip() or any(
            (ord(char) < 32 and char != "\t") or ord(char) == 127 for char in subject
        ):
            raise ValueError("invalid backlog subject")


def build_alert(report: dict, run_date: str, iso_week: str) -> dict:
    """Return a typed decision; only the shell wrapper may publish an alert."""
    validate_report(report, run_date)
    expected_week = date.fromisoformat(run_date).strftime("%G-W%V")
    if iso_week != expected_week:
        raise ValueError("ISO week disagrees with run date")
    rate = report["compliance_rate"]
    if not report["reviewable"]:
        return {"action": "no-alert", "rate": rate, "reason": "no-reviewable-commits"}
    if report["verdict"] == "PASS":
        return {"action": "no-alert", "rate": rate, "reason": "threshold-met"}
    severity = "critical" if rate < CRITICAL_BELOW else "high" if rate < HIGH_BELOW else "medium"
    dedup_key = f"compliance-alert-{iso_week}"
    # Indentation keeps arbitrary commit text literal without a closable fence.
    backlog = "\n".join(
        f"    {entry['hash']} {entry['subject']}"
        for entry in report["unreviewed_commits"]
    )
    body = f"""## Compliance Alert — {run_date}

**Compliance rate:** {rate}% | **Severity:** {severity}
**Total commits:** {report['total_commits']} | **Skipped:** {report['skipped']}
**Reviewable:** {report['reviewable']} | **Reviewed:** {report['reviewed']} | **Unreviewed:** {report['unreviewed']}
**Dashboard verdict:** {report['verdict']}
**Pass threshold:** {report['threshold']}%

### Unreviewed commits

{backlog}

### Method and limits

Rate = floor(reviewed × 100 / reviewable); policy: issue #3596, Thresholds (2026).
Counts retain the dashboard's existing commit classification and review-evidence heuristic.
Review authenticity and bypass attribution: NOT_EVALUATED; independent review is required.
Stage prompt drift events are separate diagnostics and do not supply the compliance verdict.

### Recommended actions

- Review the listed commits and record findings against their full hashes.
- Investigate classification and evidence gaps before attributing a bypass.
- Address confirmed systemic defects without changing review requirements.

Dedup key: {dedup_key}
"""
    return {
        "action": "alert", "rate": rate, "severity": severity,
        "priority_label": f"priority:{severity}", "dedup_key": dedup_key,
        "title": f"Compliance alert: {iso_week} — {rate}% ({severity})", "body": body,
    }


def unique_fields(pairs: list[tuple[str, object]]) -> dict:
    """Reject ambiguous JSON rather than accepting the last duplicate value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--week", required=True)
    args = parser.parse_args()
    try:
        alert = build_alert(json.load(sys.stdin, object_pairs_hook=unique_fields), args.date, args.week)
    except (ValueError, TypeError) as error:
        # Do not echo input data: malformed reports may contain sensitive text.
        print(f"ERROR: Invalid compliance report: {error}", file=sys.stderr)
        return 2
    # A line protocol avoids shell evaluation and preserves multiline bodies.
    for key in ("action", "rate", "severity", "priority_label", "title", "body"):
        print(alert.get(key, ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
