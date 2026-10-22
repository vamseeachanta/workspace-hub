"""Validate the dashboard's top-level JSON before cron evaluates alert policy."""

import json
import sys


def parse_report(text):
    """Read the dashboard contract; human text and nested verdicts are not metrics."""
    marker = "JSON Report:\n"
    if text.count(marker) != 1:
        raise ValueError("expected one JSON Report marker")
    payload, _ = json.JSONDecoder().raw_decode(text.split(marker, 1)[1].lstrip())
    if not isinstance(payload, dict):
        raise TypeError("report must be an object")
    fields = ("total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
              "compliance_rate", "threshold")
    for field in fields:
        value = payload.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid nonnegative integer: {field}")
    if payload["total_commits"] != payload["skipped"] + payload["reviewable"]:
        raise ValueError("total differs from skipped plus reviewable")
    if payload["reviewable"] != payload["reviewed"] + payload["unreviewed"]:
        raise ValueError("reviewable differs from reviewed plus unreviewed")
    # Source: compliance-dashboard.sh, Calculate rates (integer percentage).
    rate = (payload["reviewed"] * 100 // payload["reviewable"]
            if payload["reviewable"] else 0)
    if payload["compliance_rate"] != rate or payload["threshold"] > 100:
        raise ValueError("invalid percentage or inconsistent rate")
    verdict = "FAIL" if payload["reviewable"] and rate < payload["threshold"] else "PASS"
    if payload.get("verdict") != verdict:
        raise ValueError("verdict differs from counts and threshold")
    return payload


def main():
    try:
        payload = parse_report(sys.stdin.read())
    except (TypeError, ValueError) as error:
        print(f"Invalid compliance report: {error}", file=sys.stderr)
        return 1
    fields = ("compliance_rate", "total_commits", "reviewed", "unreviewed",
              "verdict", "reviewable")
    print("\t".join(str(payload[field]) for field in fields))
    return 0


if __name__ == "__main__":
    sys.exit(main())
