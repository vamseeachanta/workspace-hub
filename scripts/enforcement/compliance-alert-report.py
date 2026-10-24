"""Validate the dashboard's JSON before the cron wrapper evaluates an alert."""

from __future__ import annotations

import argparse
import json
import sys


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate field: {key}")
        result[key] = value
    return result


def alert_fields(text: str, dashboard_status: int) -> list[str]:
    marker = "JSON Report:\n"
    if text.count(marker) != 1:
        raise ValueError("expected one dashboard JSON report")
    payload, _ = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(
        text.split(marker, 1)[1].lstrip()
    )
    if not isinstance(payload, dict):
        raise TypeError("report must be an object")
    fields = ("total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
              "compliance_rate", "threshold")
    for field in fields:
        value = payload.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    total, skipped, reviewable, reviewed, unreviewed, rate, threshold = (
        payload[field] for field in fields
    )
    if total != skipped + reviewable or reviewable != reviewed + unreviewed:
        raise ValueError("commit counts do not reconcile")
    # Source: docs/methodology/compliance-dashboard.md, How Compliance is Calculated.
    # Match the dashboard's integer percentage; an empty denominator has no rate.
    expected_rate = reviewed * 100 // reviewable if reviewable else 0
    if rate != expected_rate or not 0 <= threshold <= 100:
        raise ValueError("invalid rate or threshold")
    verdict = "FAIL" if reviewable and rate < threshold else "PASS"
    if payload.get("verdict") != verdict:
        raise ValueError("verdict disagrees with counts and threshold")
    if dashboard_status != (1 if verdict == "FAIL" else 0):
        raise ValueError("dashboard exit status disagrees with verdict")
    state = "EVALUATED" if reviewable else "NO_REVIEWABLE"
    return [state, str(rate), str(total), str(reviewed), str(unreviewed), verdict]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard-status", type=int, required=True)
    args = parser.parse_args()
    try:
        fields = alert_fields(sys.stdin.read(), args.dashboard_status)
    except (TypeError, ValueError) as exc:
        print(f"Invalid compliance report: {exc}", file=sys.stderr)
        return 1
    print("\t".join(fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
