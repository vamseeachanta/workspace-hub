"""Validate one dashboard invocation before the cron wrapper considers alerts.

Source: compliance-dashboard.sh, Calculate rates and Determine verdict (2026).
This validates the dashboard's existing integer arithmetic, not review evidence.
"""

from __future__ import annotations

import json
import sys


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous JSON rather than silently accepting a duplicate key."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate report field")
        result[key] = value
    return result


def parse_report(output: str, status: int) -> dict[str, object]:
    """Read root metrics only; nested telemetry never supplies alert counts."""
    sections = output.split("JSON Report:\n")
    if len(sections) != 2:
        raise ValueError("expected one JSON report")
    payload, _ = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(
        sections[1].lstrip()
    )
    if not isinstance(payload, dict):
        raise TypeError("expected report object")
    fields = (
        "total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
        "compliance_rate", "threshold",
    )
    for field in fields:
        if type(payload.get(field)) is not int or payload[field] < 0:
            raise ValueError("expected nonnegative integer metric")
    if payload["threshold"] > 100:
        raise ValueError("invalid percentage threshold")
    reviewable = payload["reviewable"]
    reviewed = payload["reviewed"]
    if payload["total_commits"] != payload["skipped"] + reviewable:
        raise ValueError("inconsistent total count")
    if reviewable != reviewed + payload["unreviewed"]:
        raise ValueError("inconsistent review count")
    # Source: compliance-dashboard.sh (2026), Calculate rates. Percentage means
    # per hundred; shell integer division truncates for these nonnegative counts.
    expected_rate = reviewed * 100 // reviewable if reviewable else 0
    if payload["compliance_rate"] != expected_rate:
        raise ValueError("inconsistent compliance rate")
    expected_verdict = (
        "FAIL" if reviewable and expected_rate < payload["threshold"] else "PASS"
    )
    if payload.get("verdict") != expected_verdict:
        raise ValueError("inconsistent dashboard verdict")
    # Source: compliance-dashboard.sh (2026), Exit code based on verdict.
    if status != int(expected_verdict == "FAIL"):
        raise ValueError("dashboard execution failed or status disagrees")
    return payload


def main() -> int:
    try:
        payload = parse_report(sys.stdin.read(), int(sys.argv[1]))
    except (ValueError, TypeError, IndexError):
        # Raw dashboard content can contain arbitrary log data; do not echo it.
        print("ERROR: Invalid dashboard report or execution status", file=sys.stderr)
        return 1
    for field in (
        "compliance_rate", "total_commits", "reviewed", "unreviewed", "verdict",
        "reviewable", "skipped",
    ):
        print(payload[field])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
