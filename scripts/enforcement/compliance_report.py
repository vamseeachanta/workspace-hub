"""Validate dashboard output and emit fixed, tab-separated alert metrics.

The input contract is compliance-dashboard.sh's JSON Report section. Nested
diagnostics are deliberately excluded from alert metrics. This is monitoring,
not authentication of review evidence or permission to publish.
"""

from __future__ import annotations

import json
import sys


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def alert_metrics(output: str) -> str:
    marker = "\nJSON Report:\n"
    # Prefix permits a report section at the beginning as well as after prose.
    sections = ("\n" + output).split(marker)
    if len(sections) != 2:
        raise ValueError("expected one JSON Report section")
    section = sections[1].lstrip()
    payload, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(section)
    tail = section[end:].strip()
    if tail and (not tail.startswith("Report saved to: ") or len(tail.splitlines()) != 1):
        raise ValueError("unexpected content after report")
    if not isinstance(payload, dict):
        raise TypeError("expected a JSON object")
    fields = (
        "total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
        "compliance_rate", "threshold",
    )
    for field in fields:
        value = payload.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    total, skipped, reviewable, reviewed, unreviewed, rate, threshold = (
        payload[field] for field in fields
    )
    if total != skipped + reviewable or reviewable != reviewed + unreviewed:
        raise ValueError("commit counts do not reconcile")
    # Percentage equation: docs/methodology/compliance-dashboard.md,
    # How Compliance is Calculated (repository policy, 2026).
    expected_rate = reviewed * 100 // reviewable if reviewable else 0
    if rate != expected_rate or threshold > 100:
        raise ValueError("invalid percentage or threshold")
    verdict = "FAIL" if reviewable and rate < threshold else "PASS"
    if payload.get("verdict") != verdict:
        raise ValueError("verdict does not match counts and threshold")

    # Issue #3794 (2026-08-03), Thresholds table: 30/50/80 percent.
    # A zero denominator has no compliance observation; do not call it 0% failure.
    if not reviewable:
        severity = "not_evaluated"
    elif rate >= 80:
        severity = "pass"
    elif rate < 30:
        severity = "critical"
    elif rate < 50:
        severity = "high"
    else:
        severity = "medium"
    return "\t".join(map(str, (rate, total, reviewed, unreviewed, reviewable, verdict, severity)))


def main() -> int:
    try:
        metrics = alert_metrics(sys.stdin.read())
    except (ValueError, TypeError) as exc:
        # No raw payload in errors: reports can contain unrestricted commit text.
        print(f"Invalid compliance report: {exc}", file=sys.stderr)
        return 1
    print(metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
