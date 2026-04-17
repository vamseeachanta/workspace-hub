"""Tests for .claude/hooks/check-state-file-size-precommit.sh — TDD per #2070 plan.

Run:
    uv run --no-project python -m pytest tests/hooks/test_check_state_file_size_precommit.py -v
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "check-state-file-size-precommit.sh"


def _make_repo(tmp_path: Path) -> Path:
    """Create an isolated git repo for hook testing."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    return repo


def _stage_file(repo: Path, rel: str, size_mb: int) -> None:
    """Create a file of given size under repo and `git add` it."""
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * (size_mb * 1024 * 1024))
    subprocess.run(["git", "add", rel], cwd=repo, check=True)


def _run_hook(repo: Path, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(HOOK)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


# --- Tests from plan TDD list ---

def test_precommit_passes_under_50mb(tmp_path):
    repo = _make_repo(tmp_path)
    _stage_file(repo, ".claude/state/session-signals/small.jsonl", 1)
    r = _run_hook(repo)
    assert r.returncode == 0, r.stderr
    assert "BLOCKED" not in r.stderr


def test_precommit_warns_50_to_75mb(tmp_path):
    repo = _make_repo(tmp_path)
    _stage_file(repo, ".claude/state/session-signals/midsize.jsonl", 60)
    r = _run_hook(repo)
    assert r.returncode == 0, r.stderr
    assert "WARN" in r.stderr
    assert "60MB" in r.stderr


def test_precommit_blocks_over_75mb(tmp_path):
    repo = _make_repo(tmp_path)
    _stage_file(repo, ".claude/state/session-signals/huge.jsonl", 80)
    r = _run_hook(repo)
    assert r.returncode == 1, r.stderr
    assert "BLOCKED" in r.stderr


def test_precommit_ignores_outside_watch(tmp_path):
    repo = _make_repo(tmp_path)
    # 80 MB file outside the watched prefix should NOT trigger the hook
    _stage_file(repo, "data/big.bin", 80)
    r = _run_hook(repo)
    assert r.returncode == 0, r.stderr
    assert "BLOCKED" not in r.stderr


def test_precommit_reads_staged_blob_size(tmp_path):
    """Plan acceptance criterion: hook must read STAGED blob, not working-tree stat.

    A developer who runs `git add huge` then truncates the working-tree file
    must still be blocked — the staged blob is what enters the repo on commit.
    """
    repo = _make_repo(tmp_path)
    rel = ".claude/state/session-signals/sneaky.jsonl"
    _stage_file(repo, rel, 80)
    # Truncate working tree AFTER staging — staged blob is still 80 MB
    (repo / rel).write_bytes(b"x" * 1024)
    r = _run_hook(repo)
    assert r.returncode == 1, (
        f"Hook used working-tree size, not staged blob size. stderr={r.stderr}"
    )
    assert "BLOCKED" in r.stderr


def test_precommit_regression_2070(tmp_path):
    """End-to-end: stage 95 MB, attempt commit, commit must be refused."""
    repo = _make_repo(tmp_path)
    # Wire the hook into this isolated repo's pre-commit chain
    hook_target = repo / ".git" / "hooks" / "pre-commit"
    hook_target.write_text(f"#!/usr/bin/env bash\nexec bash {HOOK}\n")
    hook_target.chmod(0o755)

    # Initial baseline commit so HEAD exists
    (repo / "README.md").write_text("baseline")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    _stage_file(repo, ".claude/state/session-signals/cost-tracking.jsonl", 95)
    r = subprocess.run(
        ["git", "commit", "-m", "should fail"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "BLOCKED" in (r.stderr + r.stdout)


def test_precommit_threshold_env_override(tmp_path):
    """Allow tuning thresholds without editing the hook."""
    repo = _make_repo(tmp_path)
    _stage_file(repo, ".claude/state/session-signals/probe.jsonl", 20)
    r = _run_hook(repo, env_extra={"STATE_SIZE_BLOCK_MB": "10"})
    assert r.returncode == 1
    assert "BLOCKED" in r.stderr
