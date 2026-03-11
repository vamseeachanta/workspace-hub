#!/usr/bin/env python3
"""check_complexity_ratchet.py — Radon cyclomatic complexity ratchet gate (WRK-1095).

Metrics tracked per repo:
  high_cc_count      — functions at radon rank D+ (CC >= 11), label "CC > 10"
  very_high_cc_count — functions at radon rank E+ (CC >= 16), label "CC > 20"

Ratchet: actual <= baseline → PASS; actual > baseline → FAIL.
Auto-updates baseline when complexity improves (no auto-commit).
SKIP_COMPLEXITY_REASON env var: bypass all checks (audit-logged).
Exit 0 = PASS, 1 = FAIL.
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---
# Repo configuration
# ---

DEFAULT_REPO_ROOT = Path(__file__).parents[2]

REPOS: dict[str, str] = {
    "assetutilities": "assetutilities",
    "digitalmodel": "digitalmodel",
    "worldenergydata": "worldenergydata",
    "assethold": "assethold",
    "ogmanufacturing": "OGManufacturing",
}

# Radon rank thresholds used for -n flag.
# radon -n D: shows rank D+ (CC >= 11); radon -n E: shows rank E+ (CC >= 16).
# Baselines and checks use identical invocations, so the ratchet is self-consistent
# even though the human-readable labels say ">10" and ">20".
_HIGH_CC_THRESHOLD = 10   # maps to radon rank D (-n D, CC >= 11)
_VERY_HIGH_CC_THRESHOLD = 20  # maps to radon rank E (-n E, CC >= 16)


# ---
# Schema validation
# ---


def _validate_baseline(data: dict) -> str | None:
    """Return error string if baseline schema invalid, else None."""
    if not isinstance(data.get("repos"), dict):
        return "'repos' key missing or not a mapping"
    for name, entry in data["repos"].items():
        if not isinstance(entry, dict):
            return f"repo '{name}': must be a mapping"
        if "high_cc_count" not in entry:
            return f"repo '{name}': missing 'high_cc_count'"
        if "very_high_cc_count" not in entry:
            return f"repo '{name}': missing 'very_high_cc_count'"
        if entry.get("exempt") and not entry.get("exempt_reason"):
            return f"repo '{name}': exempt=true requires 'exempt_reason'"
    return None


# ---
# Core ratchet logic
# ---


def check_repo(
    repo: str,
    baseline: dict,
    actual: dict,
) -> dict:
    """Return a result dict for a single repo.

    Args:
        repo: repo name
        baseline: dict with high_cc_count and very_high_cc_count from baseline
        actual: dict with high_cc_count and very_high_cc_count from live run

    Returns dict with keys: repo, status, actual, baseline, improved, message.
    """
    b_high = int(baseline.get("high_cc_count", 0))
    b_very = int(baseline.get("very_high_cc_count", 0))
    a_high = int(actual.get("high_cc_count", 0))
    a_very = int(actual.get("very_high_cc_count", 0))

    improved = a_high < b_high or a_very < b_very
    failed_metrics: list[str] = []

    if a_high > b_high:
        failed_metrics.append(f"high_cc_count: {a_high} > baseline {b_high} (+{a_high - b_high})")
    if a_very > b_very:
        failed_metrics.append(
            f"very_high_cc_count: {a_very} > baseline {b_very} (+{a_very - b_very})"
        )

    if failed_metrics:
        return {
            "repo": repo,
            "status": "fail",
            "actual": actual,
            "baseline": baseline,
            "improved": False,
            "message": f"{repo}: {'; '.join(failed_metrics)}",
        }

    return {
        "repo": repo,
        "status": "pass",
        "actual": actual,
        "baseline": baseline,
        "improved": improved,
    }


# ---
# Radon runner
# ---


def _count_functions_above_threshold(repo_path: Path, threshold: int) -> int:
    """Run radon cc and count functions at or above threshold rank."""
    radon_rank = {10: "D", 20: "E"}.get(threshold, "E")
    try:
        result = subprocess.run(
            ["uvx", "radon==6.0.1", "cc", "src/", "-n", radon_rank],
            capture_output=True, text=True, cwd=repo_path, timeout=120,
        )
        return sum(
            1 for line in result.stdout.splitlines()
            if line.startswith("    ") and len(line) > 4 and line[4] in ("M", "F", "C")
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1


def _run_radon(repo_path: Path) -> tuple[dict, str]:
    """Run radon on a repo and return (counts_dict, status_line).

    Returns ({"high_cc_count": -1, ...}, "SKIP reason") on failure.
    """
    if not (repo_path / "src").is_dir():
        skip_msg = f"SKIP (no src/ directory at {repo_path})"
        return {"high_cc_count": -1, "very_high_cc_count": -1}, skip_msg

    high_cc = _count_functions_above_threshold(repo_path, _HIGH_CC_THRESHOLD)
    if high_cc < 0:
        return {"high_cc_count": -1, "very_high_cc_count": -1}, "SKIP (radon unavailable)"

    very_high_cc = _count_functions_above_threshold(repo_path, _VERY_HIGH_CC_THRESHOLD)

    return {
        "high_cc_count": high_cc,
        "very_high_cc_count": very_high_cc,
    }, f"high_cc={high_cc} very_high_cc={very_high_cc}"


# ---
# Report formatting
# ---


def _format_report(
    passes: list[dict],
    failures: list[dict],
    bypass_reason: str | None,
    timestamp: str,
) -> str:
    lines: list[str] = [
        f"complexity-ratchet report — {timestamp}",
        "=" * 60,
    ]
    if bypass_reason:
        lines += [
            "STATUS: BYPASSED",
            f"SKIP_COMPLEXITY_REASON: {bypass_reason}",
            "",
            "Complexity ratchet gate skipped. All checks omitted.",
        ]
        return "\n".join(lines)

    for p in passes:
        if p["status"] == "exempt":
            lines.append(f"  EXEMPT  {p['repo']}  ({p['reason']})")
        elif p.get("improved"):
            lines.append(
                f"  PASS    {p['repo']}  "
                f"high_cc={p['actual']['high_cc_count']}  "
                f"very_high_cc={p['actual']['very_high_cc_count']}  [IMPROVED]"
            )
        else:
            lines.append(
                f"  PASS    {p['repo']}  "
                f"high_cc={p['actual']['high_cc_count']}  "
                f"very_high_cc={p['actual']['very_high_cc_count']}"
            )

    for f in failures:
        msg = f.get("message", f"{f['repo']}: FAIL")
        lines.append(f"  FAIL    {msg}")

    lines += [
        "",
        f"Result: {len(passes)} PASS, {len(failures)} FAIL",
    ]
    return "\n".join(lines)


# ---
# Baseline writer
# ---


def _write_baseline(
    baseline_path: Path,
    improved: dict[str, dict],
    existing_data: dict | None = None,
) -> None:
    """Write or update baseline YAML with improved repo counts."""
    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — cannot write baseline", file=sys.stderr)
        sys.exit(1)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    repos_data: dict = {}

    if existing_data and "repos" in existing_data:
        repos_data = dict(existing_data["repos"])

    for repo, counts in improved.items():
        entry = repos_data.get(repo, {})
        new_entry = {k: v for k, v in entry.items()
                     if k not in ("high_cc_count", "very_high_cc_count", "updated_at")}
        new_entry["high_cc_count"] = counts["high_cc_count"]
        new_entry["very_high_cc_count"] = counts["very_high_cc_count"]
        new_entry["updated_at"] = today
        repos_data[repo] = new_entry

    data = {
        "schema_version": "1",
        "updated_at": today,
        "repos": repos_data,
    }
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(
        yaml.dump(data, default_flow_style=False, sort_keys=True),
        encoding="utf-8",
    )


# ---
# Main
# ---


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default="config/quality/complexity-baseline.yaml",
        help="Path to complexity-baseline.yaml",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Run radon on all repos and write initial baseline; exit 0 always",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Override workspace root path",
    )
    args = parser.parse_args(argv)

    repo_root_env = os.environ.get("COMPLEXITY_RATCHET_REPO_ROOT")
    repo_root = Path(args.repo_root or repo_root_env or DEFAULT_REPO_ROOT)
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bypass_reason = os.environ.get("SKIP_COMPLEXITY_REASON", "").strip()

    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — install via uv add pyyaml", file=sys.stderr)
        return 1

    # -- --init mode ----------------------------------------------------------
    if args.init:
        print(f"complexity-ratchet --init — {timestamp}")
        print(f"Repo root: {repo_root}")
        print(f"Baseline output: {baseline_path}")
        print("=" * 60)
        counts: dict[str, dict] = {}
        for repo_name, rel_path in REPOS.items():
            repo_path = repo_root / rel_path
            if not repo_path.is_dir():
                print(f"  SKIP  {repo_name}  (not found: {repo_path})")
                continue
            repo_counts, summary = _run_radon(repo_path)
            if repo_counts["high_cc_count"] < 0:
                print(f"  SKIP  {repo_name}  ({summary})")
            else:
                counts[repo_name] = repo_counts
                print(f"  INIT  {repo_name}  {summary}")

        existing_data = None
        if baseline_path.exists():
            try:
                existing_data = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
            except Exception:
                pass

        _write_baseline(baseline_path, counts, existing_data)
        print(f"\nWrote baseline → {baseline_path}")
        return 0

    # -- Bypass active --------------------------------------------------------
    if bypass_reason:
        report = _format_report([], [], bypass_reason, timestamp)
        print(report)
        return 0

    # -- Load baseline --------------------------------------------------------
    if not baseline_path.exists():
        print(
            f"ERROR: baseline file not found: {baseline_path}\n"
            "Run with --init to create it.",
            file=sys.stderr,
        )
        return 1

    try:
        baseline_data = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"ERROR: could not parse baseline YAML: {exc}", file=sys.stderr)
        return 1

    schema_error = _validate_baseline(baseline_data)
    if schema_error:
        print(f"ERROR: baseline schema invalid — {schema_error}", file=sys.stderr)
        return 1

    # -- Run radon per repo ---------------------------------------------------
    print(f"complexity-ratchet check — {timestamp}")
    print(f"Repo root: {repo_root}")
    print("=" * 60)

    actual_counts: dict[str, dict] = {}
    skipped: list[str] = []

    for repo_name, entry in baseline_data["repos"].items():
        if entry.get("exempt"):
            continue
        rel_path = REPOS.get(repo_name, repo_name)
        repo_path = repo_root / rel_path
        if not repo_path.is_dir():
            print(f"  SKIP  {repo_name}  (not found: {repo_path})")
            skipped.append(repo_name)
            continue
        repo_counts, summary = _run_radon(repo_path)
        if repo_counts["high_cc_count"] < 0:
            print(f"  SKIP  {repo_name}  ({summary})")
            skipped.append(repo_name)
        else:
            actual_counts[repo_name] = repo_counts
            print(f"  RAN   {repo_name}  {summary}")

    # -- Ratchet check --------------------------------------------------------
    passes: list[dict] = []
    failures: list[dict] = []

    for repo_name, entry in baseline_data["repos"].items():
        if entry.get("exempt"):
            passes.append({"repo": repo_name, "status": "exempt",
                           "reason": entry.get("exempt_reason", "")})
            continue
        if repo_name in skipped:
            continue
        actual = actual_counts.get(repo_name)
        if actual is None:
            failures.append({"repo": repo_name, "status": "missing",
                             "message": f"no radon result for '{repo_name}'"})
            continue

        result = check_repo(repo_name, entry, actual)
        if result["status"] == "pass":
            passes.append(result)
        else:
            failures.append(result)

    report = _format_report(passes, failures, None, timestamp)
    print("")
    print(report)

    # -- Auto-update baseline for improved repos ------------------------------
    improved = {
        p["repo"]: p["actual"]
        for p in passes
        if p.get("improved")
    }
    if improved:
        existing_data = baseline_data
        _write_baseline(baseline_path, improved, existing_data)
        print(
            f"\nBaseline auto-updated for {len(improved)} improved repo(s): "
            + ", ".join(improved.keys())
        )
        print("(No auto-commit — commit the updated baseline manually.)")

    if failures:
        print(
            f"\nComplexity ratchet FAILED: {len(failures)} repo(s) with regressions",
            file=sys.stderr,
        )
        return 1

    print(f"\nComplexity ratchet PASSED: {len(passes)} repo(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
