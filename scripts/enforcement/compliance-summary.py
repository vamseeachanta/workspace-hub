"""Read the dashboard's top-level JSON summary, refusing incomplete evidence."""

import json
import sys


def parse_summary(output):
    """Validate the count identities emitted by compliance-dashboard.sh, main()."""
    marker = "JSON Report:\n"
    if marker not in output:
        raise ValueError("missing JSON report marker")
    report, _ = json.JSONDecoder().raw_decode(output.split(marker, 1)[1].lstrip())
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
        value = report[field]
        if type(value) is not int or value < 0:
            raise ValueError(f"invalid {field}")
    total, skipped, reviewable, reviewed, unreviewed, rate, threshold = (
        report[field] for field in fields
    )
    if total != skipped + reviewable or reviewable != reviewed + unreviewed:
        raise ValueError("inconsistent commit counts")
    # Percentage scale and integer truncation: compliance-dashboard.sh, main().
    expected = reviewed * 100 // reviewable if reviewable else 0
    if rate != expected or threshold > 100:
        raise ValueError("inconsistent percentage")
    verdict = "FAIL" if reviewable and rate < threshold else "PASS"
    if report["verdict"] != verdict:
        raise ValueError("inconsistent dashboard verdict")
    return total, reviewable, reviewed, unreviewed, rate, verdict


def main():
    try:
        values = parse_summary(sys.stdin.read())
    except (ValueError, KeyError, TypeError) as error:
        print(f"Invalid dashboard summary: {error}", file=sys.stderr)
        return 1
    print("\t".join(map(str, values)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
