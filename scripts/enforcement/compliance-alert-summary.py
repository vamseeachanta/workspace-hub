"""Validate the dashboard JSON before the cron wrapper decides to publish."""

import json
import sys


def summarize(output: str, status: int) -> str:
    """Return validated integer counters and verdict as tab-separated fields."""
    marker = "JSON Report:\n"
    if output.count(marker) != 1:
        raise ValueError("expected one dashboard JSON report")
    payload, _ = json.JSONDecoder().raw_decode(output.split(marker, 1)[1].lstrip())
    if not isinstance(payload, dict):
        raise TypeError("dashboard report must be an object")
    fields = ("total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
              "compliance_rate", "threshold")
    for field in fields:
        value = payload.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid dashboard counter: {field}")
    total, skipped, reviewable, reviewed, unreviewed, rate, threshold = (
        payload[field] for field in fields
    )
    if skipped > total or reviewable != total - skipped or reviewed + unreviewed != reviewable:
        raise ValueError("dashboard counters do not reconcile")
    # Source: docs/methodology/compliance-dashboard.md, rate definition.
    expected_rate = reviewed * 100 // reviewable if reviewable else 0
    if rate != expected_rate or threshold > 100:
        raise ValueError("dashboard rate or threshold is inconsistent")
    verdict = "FAIL" if reviewable and rate < threshold else "PASS"
    if payload.get("verdict") != verdict or status != (1 if verdict == "FAIL" else 0):
        raise ValueError("dashboard verdict or exit status is inconsistent")
    return "\t".join(map(str, (total, reviewed, unreviewed, rate, reviewable, verdict)))


def main() -> int:
    try:
        print(summarize(sys.stdin.read(), int(sys.argv[1])))
    except (ValueError, TypeError, KeyError, IndexError) as error:
        print(f"Invalid compliance report: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
