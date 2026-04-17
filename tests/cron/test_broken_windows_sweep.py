"""Tests for scripts/cron/broken-windows-sweep.sh — TDD per #2314 plan."""

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "broken-windows-sweep.sh"


def _mk_repo(base: Path, name: str, failing: list[str], passing: list[str] | None = None):
    """Create a fake tier-1 repo with a .claude/state/test-health.jsonl.

    Each failing test appears as a JSONL row {"test": "...", "status": "FAIL"};
    each passing row is {"test": "...", "status": "PASS"}. This mirrors the
    cached test-health format the sweep reads instead of re-executing pytest.
    """
    repo_dir = base / name
    state = repo_dir / ".claude" / "state"
    state.mkdir(parents=True, exist_ok=True)
    rows = [{"test": t, "status": "FAIL"} for t in failing]
    rows += [{"test": t, "status": "PASS"} for t in (passing or [])]
    (state / "test-health.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n"
    )
    return repo_dir


def _baseline(month: str, repos: dict[str, list[str]]) -> str:
    """Build a previous-month report showing `failing` tests per repo."""
    lines = [
        f"# broken-windows — {month}",
        "",
        "**Status:** GREEN — seed baseline.",
        "",
        "## Persistent failures (still failing — pre-existing)",
        "",
        "| Repo | Test | First seen |",
        "|------|------|-----------|",
    ]
    for repo, tests in repos.items():
        for t in tests:
            lines.append(f"| {repo} | {t} | 2026-03 |")
    lines.append("")
    return "\n".join(lines)


def _run(tmp_path: Path, repos: dict[str, dict], baseline: str | None):
    out_dir = tmp_path / "out"
    repos_root = tmp_path / "repos"
    repos_root.mkdir(parents=True, exist_ok=True)
    repo_pairs = []
    for name, data in repos.items():
        _mk_repo(repos_root, name, data.get("failing", []), data.get("passing", []))
        repo_pairs.append(f"{name}:{repos_root / name}")

    if baseline is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "broken-windows-2026-03.md").write_text(baseline)

    env = os.environ.copy()
    env["BROKEN_WINDOWS_OUT_DIR"] = str(out_dir)
    env["BROKEN_WINDOWS_MONTH"] = "2026-04"
    env["BROKEN_WINDOWS_PREV_MONTH"] = "2026-03"
    env["BROKEN_WINDOWS_REPOS"] = ",".join(repo_pairs)
    env["REPO_ROOT"] = str(tmp_path)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env, capture_output=True, text=True, timeout=15,
    )
    return r, out_dir / "broken-windows-2026-04.md"


def test_sweep_detects_new_failure(tmp_path):
    baseline = _baseline("2026-03", {"repo_a": ["old_fail"]})
    r, report = _run(tmp_path, {"repo_a": {"failing": ["old_fail", "new_fail"]}}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    new_section = body.split("## New failures", 1)[1].split("## ", 1)[0]
    assert "new_fail" in new_section
    assert "old_fail" not in new_section


def test_sweep_detects_resolved(tmp_path):
    baseline = _baseline("2026-03", {"repo_a": ["was_failing"]})
    r, report = _run(tmp_path, {"repo_a": {"failing": [], "passing": ["was_failing"]}}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    resolved = body.split("## Resolved failures", 1)[1].split("## ", 1)[0]
    assert "was_failing" in resolved


def test_sweep_detects_persistent(tmp_path):
    baseline = _baseline("2026-03", {"repo_a": ["persistent_fail"]})
    r, report = _run(tmp_path, {"repo_a": {"failing": ["persistent_fail"]}}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    persistent = body.split("## Persistent failures", 1)[1].split("## ", 1)[0]
    assert "persistent_fail" in persistent


def test_sweep_baseline_parsing(tmp_path):
    baseline = _baseline("2026-03", {"repo_a": ["t1", "t2", "t3"]})
    r, report = _run(tmp_path, {"repo_a": {"failing": ["t1", "t2", "t3"]}}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    # All three should be persistent, none new
    new_section = body.split("## New failures", 1)[1].split("## ", 1)[0]
    for t in ("t1", "t2", "t3"):
        assert t not in new_section


def test_sweep_status_bands(tmp_path):
    # 6 new failures → RED (block = 5)
    baseline = _baseline("2026-03", {"repo_a": []})
    r, report = _run(tmp_path, {"repo_a": {"failing": [f"t{i}" for i in range(6)]}}, baseline)
    body = report.read_text()
    assert "Status:** RED" in body


def test_sweep_handles_first_run(tmp_path):
    r, report = _run(tmp_path, {"repo_a": {"failing": ["a", "b"]}}, baseline=None)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    # First run: baseline missing → all failures are NEW
    new_section = body.split("## New failures", 1)[1].split("## ", 1)[0]
    assert "a" in new_section
    assert "b" in new_section


def test_sweep_handles_missing_repo(tmp_path):
    baseline = _baseline("2026-03", {"repo_a": []})
    # repo_ghost has no test-health.jsonl
    env = os.environ.copy()
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "broken-windows-2026-03.md").write_text(baseline)
    repos_root = tmp_path / "repos"
    repos_root.mkdir(parents=True, exist_ok=True)
    (repos_root / "repo_ghost").mkdir()

    env["BROKEN_WINDOWS_OUT_DIR"] = str(out_dir)
    env["BROKEN_WINDOWS_MONTH"] = "2026-04"
    env["BROKEN_WINDOWS_PREV_MONTH"] = "2026-03"
    env["BROKEN_WINDOWS_REPOS"] = f"repo_ghost:{repos_root / 'repo_ghost'}"
    env["REPO_ROOT"] = str(tmp_path)
    r = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=15)
    assert r.returncode == 0, r.stderr
    body = (out_dir / "broken-windows-2026-04.md").read_text()
    assert "repo_ghost" in body
    assert "no test-health" in body.lower() or "no data" in body.lower()
