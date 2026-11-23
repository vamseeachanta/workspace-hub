"""Tests for scripts/state/rotate-cost-tracking.sh — TDD per #2070 plan."""

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "state" / "rotate-cost-tracking.sh"


def _make_repo_with_file(tmp_path: Path, size_mb: int) -> tuple[Path, Path]:
    """Create an isolated git repo with a cost-tracking.jsonl of size_mb."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    src = repo / ".claude" / "state" / "session-signals" / "cost-tracking.jsonl"
    src.parent.mkdir(parents=True, exist_ok=True)
    if size_mb > 0:
        with src.open("wb") as f:
            f.write(b"x" * (size_mb * 1024 * 1024))
    return repo, src


def _stub_verifier(repo: Path, exit_code: int) -> Path:
    p = repo / "stub-verifier.sh"
    p.write_text(f"#!/usr/bin/env bash\nexit {exit_code}\n")
    p.chmod(0o755)
    return p


def _run(repo: Path, src: Path, verify_script: Path, env_extra: dict | None = None):
    env = os.environ.copy()
    env["STATE_ROTATE_SRC"] = str(src)
    env["STATE_VERIFY_SCRIPT"] = str(verify_script)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=repo, env=env, capture_output=True, text=True, timeout=30,
    )


def test_rotate_refuses_without_consumer_check(tmp_path):
    """Verifier exits 1 → rotation must refuse with exit 2."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=45)
    verifier = _stub_verifier(repo, exit_code=1)
    r = _run(repo, src, verifier)
    assert r.returncode == 2, r.stderr
    assert "REFUSED" in r.stderr
    # Source file must NOT have been touched
    assert src.exists()
    assert src.stat().st_size == 45 * 1024 * 1024


def test_rotate_creates_archive_and_truncates(tmp_path):
    """Verifier passes + 45 MB file → archive .gz exists, source is 0 bytes."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=45)
    verifier = _stub_verifier(repo, exit_code=0)
    r = _run(repo, src, verifier, env_extra={"STATE_ROTATE_DATE": "2026-04-17"})
    assert r.returncode == 0, r.stderr + r.stdout
    arc_dir = src.parent / "archive"
    assert (arc_dir / "cost-tracking-2026-04-17.jsonl.gz").is_file()
    assert src.exists()
    assert src.stat().st_size == 0


def test_rotate_no_auto_commit(tmp_path):
    """Rotation must NOT auto-commit; verify git log unchanged."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=45)
    # Baseline: no commits yet
    log_before = subprocess.run(
        ["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True
    ).stdout
    verifier = _stub_verifier(repo, exit_code=0)
    r = _run(repo, src, verifier, env_extra={"STATE_ROTATE_DATE": "2026-04-18"})
    assert r.returncode == 0
    # And output mentions the manual commit instructions
    assert "git add" in r.stdout
    assert "git commit" in r.stdout
    log_after = subprocess.run(
        ["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True
    ).stdout
    assert log_before == log_after, "Rotation auto-committed!"


def test_rotate_skips_under_30mb(tmp_path):
    """Source below ROTATE_AT_MB → no-op exit 0, no archive created."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=10)
    verifier = _stub_verifier(repo, exit_code=0)
    r = _run(repo, src, verifier)
    assert r.returncode == 0
    assert "skipping" in r.stdout.lower()
    arc_dir = src.parent / "archive"
    assert not arc_dir.exists() or not list(arc_dir.glob("*.gz"))
    # Source unchanged
    assert src.stat().st_size == 10 * 1024 * 1024


def test_rotate_refuses_duplicate_date(tmp_path):
    """If today's archive already exists, refuse with exit 3."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=45)
    verifier = _stub_verifier(repo, exit_code=0)
    arc_dir = src.parent / "archive"
    arc_dir.mkdir(parents=True, exist_ok=True)
    (arc_dir / "cost-tracking-2026-04-19.jsonl.gz").write_bytes(b"existing")
    r = _run(repo, src, verifier, env_extra={"STATE_ROTATE_DATE": "2026-04-19"})
    assert r.returncode == 3
    assert "already exists" in r.stderr
    # Source unchanged
    assert src.stat().st_size == 45 * 1024 * 1024


def test_rotate_handles_missing_source(tmp_path):
    """No source file → exit 0 with informative message (not an error)."""
    repo, src = _make_repo_with_file(tmp_path, size_mb=0)  # path computed, file not created
    assert not src.exists(), "fixture: file should not exist when size_mb=0"
    verifier = _stub_verifier(repo, exit_code=0)
    r = _run(repo, src, verifier)
    assert r.returncode == 0
    assert "nothing to do" in r.stdout.lower()
