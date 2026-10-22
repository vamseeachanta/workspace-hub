"""Validate the dashboard's JSON contract before the cron makes alert decisions."""

from __future__ import annotations

import json
import sys


class InvalidReport(ValueError):
    """The report does not satisfy the dashboard contract."""


FIELDS = (
    "compliance_rate", "total_commits", "reviewed", "unreviewed", "reviewable",
    "threshold", "verdict",
)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidReport("duplicate JSON field")
        result[key] = value
    return result


def parse_report(output: str) -> dict:
    """Read only the root report, never human text or nested event counters.

    Source: docs/methodology/compliance-dashboard.md, 'How Compliance is
    Calculated', steps 4–5. Integer percentages follow the existing dashboard
    contract. Zero reviewable commits retain its legacy zero-rate sentinel.
    """
    marker = "JSON Report:\n"
    if output.count(marker) != 1:
        raise InvalidReport("expected exactly one JSON Report section")
    decoder = json.JSONDecoder(object_pairs_hook=unique_object)
    report, _ = decoder.raw_decode(output.split(marker, 1)[1].lstrip())
    if not isinstance(report, dict):
        raise InvalidReport("report must be a JSON object")
    for field in (*FIELDS[:-1], "skipped"):
        value = report.get(field)
        if type(value) is not int or value < 0:
            raise InvalidReport(f"invalid nonnegative integer: {field}")
    if not 0 <= report["threshold"] <= 100:
        raise InvalidReport("threshold must be a percentage")
    reviewable = report["reviewable"]
    if report["total_commits"] != reviewable + report["skipped"]:
        raise InvalidReport("total does not equal reviewable plus skipped")
    if reviewable != report["reviewed"] + report["unreviewed"]:
        raise InvalidReport("reviewable does not equal reviewed plus unreviewed")
    expected_rate = report["reviewed"] * 100 // reviewable if reviewable else 0
    if report["compliance_rate"] != expected_rate:
        raise InvalidReport("rate disagrees with commit counts")
    expected_verdict = (
        "FAIL" if reviewable and expected_rate < report["threshold"] else "PASS"
    )
    if report.get("verdict") != expected_verdict:
        raise InvalidReport("verdict disagrees with counts and threshold")
    return report


def main() -> int:
    try:
        report = parse_report(sys.stdin.read())
    except ValueError as error:
        print(f"Invalid compliance report: {error}", file=sys.stderr)
        return 2
    print("\t".join(str(report[field]) for field in FIELDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
