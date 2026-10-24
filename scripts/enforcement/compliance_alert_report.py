"""Validate the dashboard's machine report before the cron wrapper alerts."""

import json
import sys


def unique_object(pairs):
    """Reject ambiguous duplicate JSON fields, including nested fields."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def parse_report(output):
    """Read exactly one marked JSON report and check accounting identities."""
    marker = "JSON Report:\n"
    if output.count(marker) != 1:
        raise ValueError("expected one JSON Report section")
    tail = output.split(marker, 1)[1].lstrip()
    report, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(tail)
    trailer = tail[end:].strip()
    if trailer and (not trailer.startswith("Report saved to: ") or "\n" in trailer):
        raise ValueError("unexpected content after JSON report")
    if not isinstance(report, dict):
        raise TypeError("report must be a JSON object")
    fields = (
        "total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
        "compliance_rate", "threshold",
    )
    for field in fields:
        value = report.get(field)
        if type(value) is not int or value < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    if report["total_commits"] != report["skipped"] + report["reviewable"]:
        raise ValueError("total must equal skipped plus reviewable")
    if report["reviewable"] != report["reviewed"] + report["unreviewed"]:
        raise ValueError("reviewable must equal reviewed plus unreviewed")
    # Source: compliance-dashboard.sh, Calculate rates (2026): integer percent.
    reviewable = report["reviewable"]
    expected_rate = report["reviewed"] * 100 // reviewable if reviewable else 0
    if report["compliance_rate"] != expected_rate:
        raise ValueError("rate does not match reviewed / reviewable")
    # Source: compliance-dashboard.sh, Determine verdict (2026).
    if report["threshold"] > 100:
        raise ValueError("threshold must be a percentage")
    expected_verdict = (
        "FAIL" if reviewable and expected_rate < report["threshold"] else "PASS"
    )
    if report.get("verdict") != expected_verdict:
        raise ValueError("verdict does not match rate and threshold")
    return report


def main():
    try:
        report = parse_report(sys.stdin.read())
        expected_exit = int(report["verdict"] == "FAIL")
        if int(sys.argv[1]) != expected_exit:
            raise ValueError("dashboard exit status does not match verdict")
    except (ValueError, TypeError, IndexError) as error:
        print(f"Invalid compliance report: {error}", file=sys.stderr)
        return 1
    fields = (
        "compliance_rate", "total_commits", "reviewed", "unreviewed", "verdict",
        "reviewable",
    )
    print("\t".join(str(report[field]) for field in fields))
    return 0


if __name__ == "__main__":
    sys.exit(main())
