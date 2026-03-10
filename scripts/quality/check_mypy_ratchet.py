#!/usr/bin/env python3
"""check_mypy_ratchet.py — Enforce per-repo mypy error count ratchet (WRK-1092).

Enforcement rule per repo:
  actual <= baseline_count  → PASS (equal or improved)
  actual >  baseline_count  → FAIL (regression)

When actual < baseline, the baseline is auto-updated (no auto-commit).

Repos marked ``exempt: true`` are skipped (require ``exempt_reason``).

If SKIP_MYPY_REASON env var is set, all checks are skipped and the
reason is logged in the report for audit trail.

Usage:
    check_mypy_ratchet.py \\
        --baseline config/quality/mypy-baseline.yaml

    check_mypy_ratchet.py \\
        --init \\
        --baseline config/quality/mypy-baseline.yaml \\
        [--repo-root /path/to/workspace-hub]

Exit codes:
    0 — all repos PASS (or bypass active, or --init mode)
    1 — one or more repos FAIL or schema error
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Repo configuration
# ---------------------------------------------------------------------------

DEFAULT_REPO_ROOT = Path(__file__).parents[2]

REPOS: dict[str, str] = {
    "assetutilities": "assetutilities",
    "digitalmodel": "digitalmodel",
    "worldenergydata": "worldenergydata",
    "assethold": "assethold",
    "ogmanufacturing": "OGManufacturing",
}


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
        if "error_count" not in entry:
            return f"repo '{name}': missing 'error_count'"
        if entry.get("exempt") and not entry.get("exempt_reason"):
            return f"repo '{name}': exempt=true requires 'exempt_reason'"
    return None


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------


def _parse_error_count(output: str) -> int:
    """Parse mypy stdout and return integer error count.

    Handles:
    - "Found N errors in M files ..."  → N
    - "Found 1 error in 1 file ..."    → 1
    - "Success: no issues found ..."   → 0
    """
    # Match "Found N error(s) in M file(s)"
    match = re.search(r"Found (\d+) errors? in \d+ files?", output)
    if match:
        return int(match.group(1))
    # "Success: no issues found"
    if re.search(r"Success:\s+no issues found", output):
        return 0
    # Fallback: count lines with ": error:"
    return output.count(": error:")


# ---------------------------------------------------------------------------
# Core ratchet logic
# ---------------------------------------------------------------------------


def check_repo(
    repo: str,
    baseline_count: int,
    actual_count: int,
) -> dict:
    """Return a result dict for a single repo.

    Returns dict with keys: repo, status, actual, baseline, improved.
    status is "pass" or "fail".
    """
    if actual_count <= baseline_count:
        return {
            "repo": repo,
            "status": "pass",
            "actual": actual_count,
            "baseline": baseline_count,
            "improved": actual_count < baseline_count,
        }
    return {
        "repo": repo,
        "status": "fail",
        "actual": actual_count,
        "baseline": baseline_count,
        "improved": False,
        "message": (
            f"{repo}: {actual_count} errors > baseline {baseline_count} "
            f"(regression of {actual_count - baseline_count})"
        ),
    }


def check_repos(
    baseline_repos: dict,
    actual_counts: dict[str, int],
) -> tuple[list[dict], list[dict]]:
    """Return (passes, failures) lists with per-repo result dicts."""
    passes: list[dict] = []
    failures: list[dict] = []

    for repo, entry in baseline_repos.items():
        if entry.get("exempt"):
            passes.append({
                "repo": repo,
                "status": "exempt",
                "reason": entry.get("exempt_reason", ""),
            })
            continue

        actual = actual_counts.get(repo)
        if actual is None:
            failures.append({
                "repo": repo,
                "status": "missing",
                "message": f"no mypy result for '{repo}'",
            })
            continue

        baseline_count = int(entry["error_count"])
        result = check_repo(repo, baseline_count, actual)
        if result["status"] == "pass":
            passes.append(result)
        else:
            failures.append(result)

    return passes, failures


# ---------------------------------------------------------------------------
# Mypy runner
# ---------------------------------------------------------------------------


def _run_mypy(repo_path: Path) -> tuple[int, str]:
    """Run mypy on a repo and return (error_count, summary_line).

    Returns (error_count, "SKIP reason") if mypy is not available.
    """
    if not (repo_path / "src").is_dir():
        return -1, f"SKIP (no src/ directory at {repo_path})"

    # Check if mypy is available
    check_cmd = ["uv", "run", "mypy", "--version"]
    try:
        proc = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )
        if proc.returncode != 0:
            return -1, "SKIP (mypy not in project venv)"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return -1, "SKIP (uv or mypy not available)"

    # Build mypy args
    mypy_args = ["uv", "run", "mypy", "src/"]
    if (repo_path / "pyproject.toml").exists():
        import re as _re
        toml_text = (repo_path / "pyproject.toml").read_text(encoding="utf-8")
        if _re.search(r"^\[tool\.mypy\]", toml_text, _re.MULTILINE):
            mypy_args += ["--config-file", "pyproject.toml"]
        else:
            mypy_args += ["--ignore-missing-imports"]
    else:
        mypy_args += ["--ignore-missing-imports"]

    try:
        proc = subprocess.run(
            mypy_args,
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=300,
        )
        combined = proc.stdout + proc.stderr
        count = _parse_error_count(combined)
        return count, combined.strip().splitlines()[-1] if combined.strip() else ""
    except subprocess.TimeoutExpired:
        return -1, "SKIP (mypy timed out after 300s)"
    except FileNotFoundError:
        return -1, "SKIP (uv not found)"


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
        f"mypy-ratchet report — {timestamp}",
        "=" * 60,
    ]
    if bypass_reason:
        lines += [
            "STATUS: BYPASSED",
            f"SKIP_MYPY_REASON: {bypass_reason}",
            "",
            "Mypy ratchet gate skipped. All checks omitted.",
        ]
        return "\n".join(lines)

    for p in passes:
        if p["status"] == "exempt":
            lines.append(f"  EXEMPT  {p['repo']}  ({p['reason']})")
        elif p.get("improved"):
            lines.append(
                f"  PASS    {p['repo']}  "
                f"actual={p['actual']}  baseline={p['baseline']}  [IMPROVED]"
            )
        else:
            lines.append(
                f"  PASS    {p['repo']}  "
                f"actual={p['actual']}  baseline={p['baseline']}"
            )

    for f in failures:
        msg = f.get("message", f"{f['repo']}: FAIL")
        lines.append(f"  FAIL    {msg}")

    lines += [
        "",
        f"Result: {len(passes)} PASS, {len(failures)} FAIL",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Baseline writer (used by --init and auto-update)
# ---------------------------------------------------------------------------


def _write_baseline(
    baseline_path: Path,
    counts: dict[str, int],
    existing_data: dict | None = None,
) -> None:
    """Write or update the baseline YAML with given error counts."""
    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — cannot write baseline", file=sys.stderr)
        sys.exit(1)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    repos_data: dict = {}

    if existing_data and "repos" in existing_data:
        repos_data = dict(existing_data["repos"])

    for repo, count in counts.items():
        entry = repos_data.get(repo, {})
        # Preserve exempt and note fields
        new_entry = {k: v for k, v in entry.items() if k not in ("error_count", "updated_at")}
        new_entry["error_count"] = count
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default="config/quality/mypy-baseline.yaml",
        help="Path to mypy-baseline.yaml (default: config/quality/mypy-baseline.yaml)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Run mypy on all repos and write initial baseline; exit 0 always",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Override workspace root path (default: two directories above this script)",
    )
    args = parser.parse_args(argv)

    repo_root_env = os.environ.get("MYPY_RATCHET_REPO_ROOT")
    repo_root = Path(args.repo_root or repo_root_env or DEFAULT_REPO_ROOT)
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bypass_reason = os.environ.get("SKIP_MYPY_REASON", "").strip()

    # -- PyYAML guard --------------------------------------------------------
    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — install it via uv add pyyaml", file=sys.stderr)
        return 1

    # -- --init mode ---------------------------------------------------------
    if args.init:
        print(f"mypy-ratchet --init — {timestamp}")
        print(f"Repo root: {repo_root}")
        print(f"Baseline output: {baseline_path}")
        print("=" * 60)
        counts: dict[str, int] = {}
        for repo_name, rel_path in REPOS.items():
            repo_path = repo_root / rel_path
            if not repo_path.is_dir():
                print(f"  SKIP  {repo_name}  (not found: {repo_path})")
                continue
            count, summary = _run_mypy(repo_path)
            if count < 0:
                print(f"  {summary.split('(')[0].strip():<8} {repo_name}")
            else:
                counts[repo_name] = count
                print(f"  INIT  {repo_name}  errors={count}")

        existing_data = None
        if baseline_path.exists():
            try:
                existing_data = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
            except Exception:
                pass

        _write_baseline(baseline_path, counts, existing_data)
        print(f"\nWrote baseline → {baseline_path}")
        return 0

    # -- Bypass active -------------------------------------------------------
    if bypass_reason:
        report = _format_report([], [], bypass_reason, timestamp)
        print(report)
        return 0

    # -- Load baseline -------------------------------------------------------
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

    # -- Run mypy per repo ---------------------------------------------------
    print(f"mypy-ratchet check — {timestamp}")
    print(f"Repo root: {repo_root}")
    print("=" * 60)

    actual_counts: dict[str, int] = {}
    skipped_repos: list[str] = []

    for repo_name in baseline_data["repos"]:
        if baseline_data["repos"][repo_name].get("exempt"):
            continue
        # Map baseline repo name to filesystem path
        rel_path = REPOS.get(repo_name, repo_name)
        repo_path = repo_root / rel_path
        if not repo_path.is_dir():
            print(f"  SKIP  {repo_name}  (not found: {repo_path})")
            skipped_repos.append(repo_name)
            continue
        count, summary = _run_mypy(repo_path)
        if count < 0:
            print(f"  {summary}")
            skipped_repos.append(repo_name)
        else:
            actual_counts[repo_name] = count
            print(f"  RAN   {repo_name}  errors={count}")

    # -- Ratchet check -------------------------------------------------------
    passes, failures = check_repos(baseline_data["repos"], actual_counts)
    report = _format_report(passes, failures, None, timestamp)
    print("")
    print(report)

    # -- Auto-update baseline for improved repos ----------------------------
    improved = {p["repo"]: p["actual"] for p in passes if p.get("improved")}
    if improved:
        existing_data = baseline_data
        _write_baseline(baseline_path, improved, existing_data)
        print(
            f"\nBaseline auto-updated for {len(improved)} improved repo(s): "
            + ", ".join(improved.keys())
        )
        print("(No auto-commit — commit the updated baseline manually.)")

    # -- Result --------------------------------------------------------------
    if failures:
        print(
            f"\nMypy ratchet FAILED: {len(failures)} repo(s) with regressions",
            file=sys.stderr,
        )
        for f in failures:
            print(f"  {f.get('message', f['repo'])}", file=sys.stderr)
        return 1

    print(f"\nMypy ratchet PASSED: {len(passes)} repo(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
