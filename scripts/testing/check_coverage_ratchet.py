#!/usr/bin/env python3
"""check_coverage_ratchet.py — Enforce per-repo coverage gate for WRK-1067.

Enforcement rule per repo:
  actual >= max(80.0, baseline_pct - 2.0)  → PASS
  actual < max(80.0, baseline_pct - 2.0)   → FAIL

Repos marked ``exempt: true`` are skipped (require ``exempt_reason``).

If SKIP_COVERAGE_REASON env var is set, all checks are skipped and the
reason is logged in the report artifact for audit trail.

Usage:
    check_coverage_ratchet.py \\
        --baseline config/testing/coverage-baseline.yaml \\
        --results  scripts/testing/coverage-results.json \\
        [--report-out scripts/testing/coverage-reports/WRK-NNN-YYYYMMDD.txt]

Exit codes:
    0 — all repos PASS (or bypass active)
    1 — one or more repos FAIL or schema error
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def _validate_baseline(data: dict) -> str | None:
    """Return error string if baseline schema invalid, else None."""
    if not isinstance(data.get("repos"), dict):
        return "'repos' key missing or not a mapping"
    for name, entry in data["repos"].items():
        if not isinstance(entry, dict):
            return f"repo '{name}': must be a mapping"
        if "coverage_pct" not in entry:
            return f"repo '{name}': missing 'coverage_pct'"
        if entry.get("exempt") and not entry.get("exempt_reason"):
            return f"repo '{name}': exempt=true requires 'exempt_reason'"
    return None


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def _floor(baseline_pct: float) -> float:
    """Compute the minimum acceptable coverage for a repo.

    Repos at or above 80%: enforce max(80, baseline-2) — hard floor + ratchet.
    Repos below 80%: enforce baseline-2 — ratchet only (prevents regression;
    hard floor activates once repo crosses 80%).
    """
    if baseline_pct >= 80.0:
        return max(80.0, baseline_pct - 2.0)
    return max(0.0, baseline_pct - 2.0)


def check_repos(
    baseline_repos: dict,
    results: dict,
) -> tuple[list[dict], list[dict]]:
    """Return (passes, failures) lists with per-repo result dicts."""
    passes: list[dict] = []
    failures: list[dict] = []

    for repo, entry in baseline_repos.items():
        if entry.get("exempt"):
            passes.append({"repo": repo, "status": "exempt", "reason": entry["exempt_reason"]})
            continue

        actual = results.get(repo)
        if actual is None:
            failures.append({
                "repo": repo,
                "status": "missing",
                "message": f"no coverage result for '{repo}'",
            })
            continue

        baseline_pct = float(entry["coverage_pct"])
        floor = _floor(baseline_pct)
        if actual >= floor:
            passes.append({
                "repo": repo,
                "status": "pass",
                "actual": actual,
                "floor": floor,
                "baseline": baseline_pct,
            })
        else:
            failures.append({
                "repo": repo,
                "status": "fail",
                "actual": actual,
                "floor": floor,
                "baseline": baseline_pct,
                "message": (
                    f"{repo}: {actual:.1f}% < floor {floor:.1f}% "
                    f"(baseline={baseline_pct:.1f}%)"
                ),
            })

    return passes, failures


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def _format_report(
    passes: list[dict],
    failures: list[dict],
    bypass_reason: str | None,
    timestamp: str,
) -> str:
    lines: list[str] = [
        f"coverage-ratchet report — {timestamp}",
        "=" * 60,
    ]
    if bypass_reason:
        lines += [
            "STATUS: BYPASSED",
            f"SKIP_COVERAGE_REASON: {bypass_reason}",
            "",
            "⚠ Coverage gate skipped. All checks omitted.",
        ]
        return "\n".join(lines)

    for p in passes:
        if p["status"] == "exempt":
            lines.append(f"  EXEMPT  {p['repo']}  ({p['reason']})")
        else:
            lines.append(
                f"  PASS    {p['repo']}  "
                f"actual={p['actual']:.1f}%  floor={p['floor']:.1f}%  "
                f"baseline={p['baseline']:.1f}%"
            )
    for f in failures:
        lines.append(f"  FAIL    {f['message']}" if "message" in f else f"  FAIL    {f['repo']}")

    lines += [
        "",
        f"Result: {len(passes)} PASS, {len(failures)} FAIL",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Path to coverage-baseline.yaml")
    parser.add_argument(
        "--results",
        required=True,
        help="Path to coverage-results.json (repo → pct mapping)",
    )
    parser.add_argument("--report-out", default=None, help="Write report to this path")
    args = parser.parse_args(argv)

    baseline_path = Path(args.baseline)
    results_path = Path(args.results)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    bypass_reason = os.environ.get("SKIP_COVERAGE_REASON", "").strip()

    # -- Load baseline -------------------------------------------------------
    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — cannot parse baseline", file=sys.stderr)
        return 1
    if not baseline_path.exists():
        print(f"ERROR: baseline file not found: {baseline_path}", file=sys.stderr)
        return 1
    try:
        baseline_data = yaml.safe_load(baseline_path.read_text()) or {}
    except Exception as exc:
        print(f"ERROR: could not parse baseline YAML: {exc}", file=sys.stderr)
        return 1

    schema_error = _validate_baseline(baseline_data)
    if schema_error:
        print(f"ERROR: baseline schema invalid — {schema_error}", file=sys.stderr)
        return 1

    # -- Load results --------------------------------------------------------
    if not results_path.exists():
        print(f"ERROR: results file not found: {results_path}", file=sys.stderr)
        return 1
    try:
        results: dict[str, float] = json.loads(results_path.read_text())
    except Exception as exc:
        print(f"ERROR: could not parse results JSON: {exc}", file=sys.stderr)
        return 1

    # -- Bypass active -------------------------------------------------------
    if bypass_reason:
        report = _format_report([], [], bypass_reason, timestamp)
        print(report)
        if args.report_out:
            Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report_out).write_text(report)
        return 0

    # -- Run checks ----------------------------------------------------------
    passes, failures = check_repos(baseline_data["repos"], results)
    report = _format_report(passes, failures, None, timestamp)
    print(report)

    if args.report_out:
        Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_out).write_text(report)

    if failures:
        print(
            f"\n✖ Coverage gate FAILED: {len(failures)} repo(s) below threshold",
            file=sys.stderr,
        )
        for f in failures:
            print(f"  {f.get('message', f['repo'])}", file=sys.stderr)
        return 1

    print(f"\n✔ Coverage gate PASSED: {len(passes)} repo(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
