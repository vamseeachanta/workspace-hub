"""Validate the dashboard's JSON report before the cron wrapper can alert."""

import json
import sys


def parse_report(output: str, status: int) -> dict:
    """Use the dashboard's top-level metrics, never nested event verdicts.

    Source: compliance-dashboard.sh, Main Analysis and Machine-readable output.
    Counts partition total = skipped + reviewed + unreviewed. The percentage
    uses integer floor division, matching that script's shell arithmetic.
    """
    marker = "JSON Report:\n"
    if marker not in output:
        raise ValueError("dashboard JSON report is missing")
    # Subjects in the human-readable preamble can render forged earlier markers.
    report, _ = json.JSONDecoder().raw_decode(output.rsplit(marker, 1)[1].lstrip())
    if not isinstance(report, dict):
        raise TypeError("dashboard report must be an object")
    fields = (
        "total_commits",
        "skipped",
        "reviewable",
        "reviewed",
        "unreviewed",
        "compliance_rate",
        "threshold",
    )
    for field in fields:
        if type(report.get(field)) is not int or report[field] < 0:
            raise ValueError(f"invalid dashboard field: {field}")
    # Percentage scale and equation: compliance-dashboard.sh, Calculate rates.
    if report["threshold"] > 100 or report["compliance_rate"] > 100:
        raise ValueError("dashboard percentage is out of range")
    reviewable = report["reviewable"]
    if report["reviewed"] + report["unreviewed"] != reviewable:
        raise ValueError("dashboard review counts do not reconcile")
    if reviewable + report["skipped"] != report["total_commits"]:
        raise ValueError("dashboard total count does not reconcile")
    expected_rate = report["reviewed"] * 100 // reviewable if reviewable else 0
    if report["compliance_rate"] != expected_rate:
        raise ValueError("dashboard rate does not match counts")
    failed = bool(reviewable and expected_rate < report["threshold"])
    expected_verdict = "FAIL" if failed else "PASS"
    if report.get("verdict") != expected_verdict or status != int(failed):
        raise ValueError("dashboard verdict or exit status does not match metrics")
    return report


def main() -> int:
    try:
        report = parse_report(sys.stdin.read(), int(sys.argv[1]))
    except (ValueError, TypeError, IndexError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    fields = (
        "total_commits",
        "reviewed",
        "unreviewed",
        "reviewable",
        "compliance_rate",
        "threshold",
        "verdict",
    )
    print("\t".join(str(report[field]) for field in fields))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
