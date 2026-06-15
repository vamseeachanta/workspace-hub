#!/usr/bin/env python3
"""check_ruff_ratchet.py — Enforce per-repo ruff error count ratchet (#3146).

Sibling of check_mypy_ratchet.py (WRK-1092). ruff is the only check-all gate
that lacked a baseline, making the pre-push gate unpassable on tier-1 repos
that carry ruff debt (worldenergydata/assetutilities/assethold). This ratchets
ruff like mypy/complexity: existing debt is baselined; only NEW errors fail.

Enforcement rule per repo:
  actual <= baseline_count  → PASS (equal or improved)
  actual >  baseline_count  → FAIL (regression)

When actual < baseline, the baseline is auto-updated (no auto-commit).
Repos marked ``exempt: true`` are skipped (require ``exempt_reason``).
If SKIP_RUFF_REASON env var is set, all checks are skipped (audited).

Usage:
    check_ruff_ratchet.py --baseline config/quality/ruff-baseline.yaml
    check_ruff_ratchet.py --init --baseline config/quality/ruff-baseline.yaml \\
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from scripts.lib.tier1_repos import resolve_tier1_repo_path, tier1_python_repos

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


DEFAULT_REPO_ROOT = Path(__file__).parents[2]
REPOS: dict[str, str] = {s: s for s in tier1_python_repos()}


def _repo_path(repo_root: Path, repo_name: str) -> Path:
    try:
        return resolve_tier1_repo_path(repo_name, repo_root=repo_root)
    except FileNotFoundError:
        return repo_root / REPOS.get(repo_name, repo_name)


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


def _parse_error_count(output: str) -> int:
    """Parse ruff output and return integer error count.

    Handles:
    - "Found N errors." / "Found 1 error."  → N
    - "All checks passed!"                   → 0
    - fallback: 0 (ruff prints findings then the Found line; absence ⇒ clean)
    """
    match = re.search(r"Found (\d+) errors?", output)
    if match:
        return int(match.group(1))
    if "All checks passed" in output:
        return 0
    return 0


def check_repo(repo: str, baseline_count: int, actual_count: int) -> dict:
    """Return a result dict for a single repo (status pass|fail)."""
    if actual_count <= baseline_count:
        return {
            "repo": repo, "status": "pass", "actual": actual_count,
            "baseline": baseline_count, "improved": actual_count < baseline_count,
        }
    return {
        "repo": repo, "status": "fail", "actual": actual_count,
        "baseline": baseline_count, "improved": False,
        "message": (
            f"{repo}: {actual_count} ruff errors > baseline {baseline_count} "
            f"(regression of {actual_count - baseline_count})"
        ),
    }


def check_repos(baseline_repos: dict, actual_counts: dict[str, int]) -> tuple[list[dict], list[dict]]:
    """Return (passes, failures) lists with per-repo result dicts."""
    passes: list[dict] = []
    failures: list[dict] = []
    for repo, entry in baseline_repos.items():
        if entry.get("exempt"):
            passes.append({"repo": repo, "status": "exempt", "reason": entry.get("exempt_reason", "")})
            continue
        actual = actual_counts.get(repo)
        if actual is None:
            failures.append({"repo": repo, "status": "missing", "message": f"no ruff result for '{repo}'"})
            continue
        result = check_repo(repo, int(entry["error_count"]), actual)
        (passes if result["status"] == "pass" else failures).append(result)
    return passes, failures


def _run_ruff(repo_path: Path) -> tuple[int, str]:
    """Run ruff on a repo and return (error_count, summary_line).

    Mirrors check-all.sh run_ruff: `uv tool run ruff check .` with the repo's
    pyproject config. Returns (-1, "SKIP ...") when ruff can't run.
    """
    args = ["uv", "tool", "run", "ruff", "check", "."]
    if (repo_path / "pyproject.toml").exists():
        args += ["--config", "pyproject.toml"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, cwd=repo_path, timeout=300)
    except subprocess.TimeoutExpired:
        return -1, "SKIP (ruff timed out after 300s)"
    except FileNotFoundError:
        return -1, "SKIP (uv not found)"
    combined = (proc.stdout + proc.stderr).strip()
    count = _parse_error_count(combined)
    last = combined.splitlines()[-1] if combined else ""
    return count, last


def _write_baseline(baseline_path: Path, counts: dict[str, int], existing_data: dict | None = None) -> None:
    """Write or update the baseline YAML with given error counts."""
    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — cannot write baseline", file=sys.stderr)
        sys.exit(1)
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    repos_data: dict = dict(existing_data["repos"]) if existing_data and "repos" in existing_data else {}
    for repo, count in counts.items():
        entry = repos_data.get(repo, {})
        new_entry = {k: v for k, v in entry.items() if k not in ("error_count", "updated_at")}
        new_entry["error_count"] = count
        new_entry["updated_at"] = today
        repos_data[repo] = new_entry
    data = {"schema_version": "1", "updated_at": today, "repos": repos_data}
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=True), encoding="utf-8")


def _format_report(passes: list[dict], failures: list[dict], bypass_reason: str | None, timestamp: str) -> str:
    lines = [f"ruff-ratchet report — {timestamp}", "=" * 60]
    if bypass_reason:
        lines += ["STATUS: BYPASSED", f"SKIP_RUFF_REASON: {bypass_reason}", "", "Ruff ratchet gate skipped."]
        return "\n".join(lines)
    for p in passes:
        if p["status"] == "exempt":
            lines.append(f"  EXEMPT  {p['repo']}  ({p['reason']})")
        else:
            tag = "  [IMPROVED]" if p.get("improved") else ""
            lines.append(f"  PASS    {p['repo']}  actual={p['actual']}  baseline={p['baseline']}{tag}")
    for f in failures:
        lines.append(f"  FAIL    {f.get('message', f['repo'] + ': FAIL')}")
    lines += ["", f"Result: {len(passes)} PASS, {len(failures)} FAIL"]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="config/quality/ruff-baseline.yaml")
    parser.add_argument("--init", action="store_true",
                        help="Run ruff on all repos and write initial baseline; exit 0")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root or os.environ.get("RUFF_RATCHET_REPO_ROOT") or DEFAULT_REPO_ROOT)
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = repo_root / baseline_path
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bypass_reason = os.environ.get("SKIP_RUFF_REASON", "").strip()

    if not _YAML_AVAILABLE:
        print("ERROR: PyYAML not available — install via uv add pyyaml", file=sys.stderr)
        return 1

    if args.init:
        print(f"ruff-ratchet --init — {timestamp}\nRepo root: {repo_root}\nBaseline: {baseline_path}\n" + "=" * 60)
        counts: dict[str, int] = {}
        for repo_name in REPOS:
            repo_path = _repo_path(repo_root, repo_name)
            if not repo_path.is_dir():
                print(f"  SKIP  {repo_name}  (not found: {repo_path})")
                continue
            count, summary = _run_ruff(repo_path)
            if count < 0:
                print(f"  {summary.split('(')[0].strip():<8} {repo_name}")
            else:
                counts[repo_name] = count
                print(f"  INIT  {repo_name}  errors={count}")
        existing = None
        if baseline_path.exists():
            try:
                existing = yaml.safe_load(baseline_path.read_text(encoding="utf-8")) or {}
            except Exception:
                pass
        _write_baseline(baseline_path, counts, existing)
        print(f"\nWrote baseline → {baseline_path}")
        return 0

    if bypass_reason:
        print(_format_report([], [], bypass_reason, timestamp))
        return 0

    if not baseline_path.exists():
        print(f"ERROR: baseline file not found: {baseline_path}\nRun with --init to create it.", file=sys.stderr)
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

    print(f"ruff-ratchet check — {timestamp}\nRepo root: {repo_root}\n" + "=" * 60)
    actual_counts: dict[str, int] = {}
    for repo_name in baseline_data["repos"]:
        if baseline_data["repos"][repo_name].get("exempt"):
            continue
        repo_path = _repo_path(repo_root, repo_name)
        if not repo_path.is_dir():
            print(f"  SKIP  {repo_name}  (not found: {repo_path})")
            continue
        count, summary = _run_ruff(repo_path)
        if count < 0:
            print(f"  {summary}")
        else:
            actual_counts[repo_name] = count
            print(f"  RAN   {repo_name}  errors={count}")

    passes, failures = check_repos(baseline_data["repos"], actual_counts)
    print("\n" + _format_report(passes, failures, None, timestamp))

    improved = {p["repo"]: p["actual"] for p in passes if p.get("improved")}
    if improved:
        _write_baseline(baseline_path, improved, baseline_data)
        print(f"\nBaseline auto-updated for {len(improved)} improved repo(s): " + ", ".join(improved))
        print("(No auto-commit — commit the updated baseline manually.)")

    if failures:
        print(f"\nRuff ratchet FAILED: {len(failures)} repo(s) with regressions", file=sys.stderr)
        return 1
    print(f"\nRuff ratchet PASSED: {len(passes)} repo(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
