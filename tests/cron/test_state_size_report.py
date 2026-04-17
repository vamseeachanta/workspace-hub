"""Tests for scripts/cron/state-size-report.sh — TDD per #2070 plan."""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "state-size-report.sh"


def _make_repo_with_state_files(tmp_path: Path, files: dict[str, int]) -> Path:
    """Create a repo with tracked state files of given sizes (in MB)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    for rel, mb in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("wb") as f:
            f.write(b"x" * (mb * 1024 * 1024))
        subprocess.run(["git", "add", rel], cwd=repo, check=True)
    if files:
        subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)
    return repo


def _run(repo: Path, env_extra: dict | None = None) -> tuple[subprocess.CompletedProcess, Path]:
    out_dir = repo / "out"
    env = os.environ.copy()
    env["STATE_REPORT_REPO_ROOT"] = str(repo)
    env["STATE_REPORT_OUT_DIR"] = str(out_dir)
    env["STATE_REPORT_WEEK"] = "2026-W16"
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=repo, env=env, capture_output=True, text=True, timeout=30,
    )
    return r, out_dir / "state-size-2026-W16.md"


def test_size_report_lists_top_10(tmp_path):
    """Plan acceptance: report contains a top-10 markdown table."""
    files = {f".claude/state/session-signals/file{i:02d}.jsonl": i for i in range(1, 12)}
    repo = _make_repo_with_state_files(tmp_path, files)
    r, report = _run(repo)
    assert r.returncode == 0, r.stderr
    assert report.is_file()
    body = report.read_text()
    assert "## Top 10 largest tracked files" in body
    # Should list at most 10 rows (between the table header and next section)
    table = body.split("## Top 10 largest tracked files", 1)[1].split("## Source", 1)[0]
    rows = [ln for ln in table.splitlines() if ln.startswith("| ") and "Size (MB)" not in ln and "----" not in ln]
    assert 1 <= len(rows) <= 10, f"expected ≤10 rows, got {len(rows)}"


def test_size_report_status_green_when_all_small(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/small.jsonl": 5}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    assert "Status:** GREEN" in report.read_text()


def test_size_report_status_yellow_when_warn(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/mid.jsonl": 60}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** YELLOW" in body
    assert "over warn" in body


def test_size_report_status_red_when_over_block(tmp_path):
    repo = _make_repo_with_state_files(
        tmp_path, {".claude/state/session-signals/huge.jsonl": 80}
    )
    r, report = _run(repo)
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** RED" in body
    assert "OVER BLOCK" in body


def test_size_report_handles_empty_state_dir(tmp_path):
    """No tracked state files → still produce a report with totals=0, status GREEN."""
    repo = _make_repo_with_state_files(tmp_path, {})
    # Need at least one commit for git ls-files to work cleanly
    (repo / "README.md").write_text("baseline")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "baseline"], cwd=repo, check=True)
    r, report = _run(repo)
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** GREEN" in body
    assert "0 files" in body
