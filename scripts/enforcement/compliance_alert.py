"""Validate one dashboard report before the cron wrapper decides to alert.

Input is the existing human + JSON output of compliance-dashboard.sh. Output is
one whitespace-delimited row of validated fields for compliance-cron.sh. Raw
input and JSON parser diagnostics are never copied to error messages.
"""

from __future__ import annotations

import argparse
import json
import sys

# Source: issue #3927, Thresholds (2026-09-28), and issue #2031,
# implementation summary (2026-04-09). These are reporting policy boundaries.
CRITICAL_BELOW = 30
HIGH_BELOW = 50


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def reject_constant(_value: str) -> None:
    raise ValueError("nonfinite JSON number")


def evaluate_output(output: str, dashboard_status: int) -> list[str]:
    """Return status, rate, counts, verdict, threshold and severity, or reject."""
    marker = "JSON Report:\n"  # compliance-dashboard.sh, machine-readable output.
    if output.count(marker) != 1:
        raise ValueError("expected one JSON Report section")
    tail = output.split(marker, 1)[1].lstrip()
    try:
        report, end = json.JSONDecoder(
            object_pairs_hook=unique_object, parse_constant=reject_constant,
        ).raw_decode(tail)
    except json.JSONDecodeError:
        raise ValueError("invalid dashboard JSON") from None
    remainder = tail[end:].strip()
    if remainder and not (
        remainder.startswith("Report saved to: ") and "\n" not in remainder
    ):
        raise ValueError("unexpected content after dashboard JSON")
    if not isinstance(report, dict):
        raise TypeError("dashboard JSON must be an object")

    fields = (
        "total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
        "compliance_rate", "threshold",
    )
    for field in fields:
        if type(report.get(field)) is not int or report[field] < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    total, skipped, reviewable, reviewed, unreviewed, rate, threshold = (
        report[field] for field in fields
    )
    if total != skipped + reviewable or reviewable != reviewed + unreviewed:
        raise ValueError("inconsistent commit counts")
    # Source: compliance-dashboard.sh, main, Calculate rates. The factor 100
    # converts a fraction to percent; integer division matches its shell output.
    expected_rate = reviewed * 100 // reviewable if reviewable else 0
    if rate != expected_rate or not 0 <= threshold <= 100:
        raise ValueError("inconsistent percentage or invalid threshold")
    # Source: compliance-dashboard.sh, main, Determine verdict. An empty
    # denominator keeps its legacy zero placeholder and PASS, but cannot alert.
    expected_verdict = "FAIL" if reviewable and rate < threshold else "PASS"
    if report.get("verdict") != expected_verdict:
        raise ValueError("inconsistent dashboard verdict")
    expected_status = int(expected_verdict == "FAIL")
    if dashboard_status != expected_status:
        raise ValueError("dashboard exit status does not match verdict")

    status, severity = "PASS", "none"
    if not reviewable:
        status = "EMPTY"
    elif expected_verdict == "FAIL":
        status = "ALERT"
        severity = (
            "critical" if rate < CRITICAL_BELOW else
            "high" if rate < HIGH_BELOW else "medium"
        )
    return [str(value) for value in (
        status, rate, total, reviewed, unreviewed, expected_verdict, threshold, severity,
    )]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard-status", type=int, required=True)
    args = parser.parse_args()
    try:
        fields = evaluate_output(sys.stdin.read(), args.dashboard_status)
    except (ValueError, TypeError) as error:
        print(f"NOT_EVALUATED: {error}", file=sys.stderr)
        return 1
    print(" ".join(fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
