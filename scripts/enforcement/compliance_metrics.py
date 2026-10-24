"""Validate the dashboard's top-level JSON before the alert wrapper uses it.

Source: compliance-dashboard.sh, main (count identities and integer rate),
and issue 3830, Thresholds (2026-09-07). No review evidence is inferred here.
"""

import json
import sys


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def parse_metrics(output, status):
    """Return validated metrics; missing evidence is an error, never a zero."""
    _, marker, tail = output.partition("JSON Report:\n")
    if not marker:
        raise ValueError("missing dashboard JSON report")
    report, _ = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(
        tail.lstrip()
    )
    if not isinstance(report, dict):
        raise TypeError("dashboard report must be an object")
    fields = ("total_commits", "skipped", "reviewable", "reviewed",
              "unreviewed", "compliance_rate", "threshold")
    for field in fields:
        value = report.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    if report["threshold"] > 100:  # Percent scale, dashboard main.
        raise ValueError("threshold exceeds 100 percent")
    eligible = report["reviewable"]
    if report["total_commits"] != report["skipped"] + eligible:
        raise ValueError("total_commits must equal skipped + reviewable")
    if eligible != report["reviewed"] + report["unreviewed"]:
        raise ValueError("reviewable must equal reviewed + unreviewed")
    # Dashboard main: integer percentage; zero is its legacy empty sentinel.
    rate = report["reviewed"] * 100 // eligible if eligible else 0
    if report["compliance_rate"] != rate:
        raise ValueError("compliance_rate disagrees with commit counts")
    verdict = "FAIL" if eligible and rate < report["threshold"] else "PASS"
    if report.get("verdict") != verdict:
        raise ValueError("verdict disagrees with rate and threshold")
    if status != int(verdict == "FAIL"):
        raise ValueError("dashboard exit status disagrees with verdict")
    return report


def main():
    try:
        report = parse_metrics(sys.stdin.read(), int(sys.argv[1]))
    except (ValueError, TypeError, IndexError) as error:
        print(f"Invalid dashboard metrics: {error}", file=sys.stderr)
        return 1
    fields = ("total_commits", "reviewable", "reviewed", "unreviewed",
              "compliance_rate", "verdict")
    print("\t".join(str(report[field]) for field in fields))
    return 0


if __name__ == "__main__":
    sys.exit(main())
