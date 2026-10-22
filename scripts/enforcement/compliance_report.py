"""Validate the dashboard's JSON section before the cron can publish an alert."""

import json
import sys


def parse_report(output: str) -> dict:
    """Enforce the count/rate contract in compliance-dashboard.sh (2026).

    Percent arithmetic and integer truncation match that producer's Calculate
    rates section; the zero-denominator PASS matches its Determine verdict section.
    """
    marker = "JSON Report:\n"
    if marker not in output:
        raise ValueError("dashboard JSON section missing")
    report, _ = json.JSONDecoder().raw_decode(output.split(marker, 1)[1].lstrip())
    if not isinstance(report, dict):
        raise TypeError("dashboard report must be an object")
    fields = ("total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
              "compliance_rate", "threshold")
    for field in fields:
        value = report.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid nonnegative integer: {field}")
    if report["total_commits"] != report["skipped"] + report["reviewable"]:
        raise ValueError("total does not equal skipped plus reviewable")
    if report["reviewable"] != report["reviewed"] + report["unreviewed"]:
        raise ValueError("reviewable does not equal reviewed plus unreviewed")
    # Source: compliance-dashboard.sh, Calculate rates (2026); percent = 100 * ratio.
    rate = report["reviewed"] * 100 // report["reviewable"] if report["reviewable"] else 0
    if report["threshold"] > 100 or report["compliance_rate"] != rate:
        raise ValueError("invalid threshold or inconsistent compliance rate")
    verdict = "FAIL" if report["reviewable"] and rate < report["threshold"] else "PASS"
    if report.get("verdict") != verdict:
        raise ValueError("dashboard verdict contradicts counts and threshold")
    return report


def main() -> int:
    try:
        report = parse_report(sys.stdin.read())
    except (ValueError, TypeError) as error:
        print(f"Invalid compliance report: {error}", file=sys.stderr)
        return 1
    fields = ("compliance_rate", "total_commits", "reviewed", "unreviewed",
              "reviewable", "skipped", "verdict", "threshold")
    print("\t".join(str(report[field]) for field in fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
