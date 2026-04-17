"""Tests for .claude/hooks/check-state-file-size-prepush.sh — TDD per #2070 plan.

Run:
    uv run --no-project python -m pytest tests/hooks/test_check_state_file_size_prepush.py -v
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "check-state-file-size-prepush.sh"
ZERO_OID = "0" * 40


def _git(repo: Path, *args: str, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, **kw)


def _make_repo_with_remote(tmp_path: Path) -> tuple[Path, Path]:
    """Local repo + bare 'remote' so push refspecs make sense."""
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    repo = tmp_path / "local"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _git(repo, "remote", "add", "origin", str(remote))
    # baseline commit + push so remote has a head
    (repo / "README.md").write_text("baseline")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "init")
    _git(repo, "push", "-q", "origin", "main")
    return repo, remote


def _commit_state_file(repo: Path, rel: str, size_mb: int, msg: str) -> str:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * (size_mb * 1024 * 1024))
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _run_prepush(
    repo: Path, stdin: str, env_extra: dict | None = None
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(HOOK)],
        cwd=repo,
        input=stdin,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


# --- Tests from plan TDD list ---

def test_prepush_passes_clean_range(tmp_path):
    """Normal small commits should pass."""
    repo, _ = _make_repo_with_remote(tmp_path)
    sha = _commit_state_file(repo, ".claude/state/session-signals/small.jsonl", 1, "small")
    remote_sha = _git(repo, "rev-parse", "origin/main").stdout.strip()
    stdin = f"refs/heads/main {sha} refs/heads/main {remote_sha}\n"
    r = _run_prepush(repo, stdin)
    assert r.returncode == 0, r.stderr
    assert "BLOCKED" not in r.stderr


def test_prepush_blocks_unstaged_pushed_blob(tmp_path):
    """The Codex P1 case: nothing staged at push time, but commit range
    contains an oversized state-signal blob — must be blocked."""
    repo, _ = _make_repo_with_remote(tmp_path)
    big_sha = _commit_state_file(
        repo, ".claude/state/session-signals/cost-tracking.jsonl", 80, "oversized"
    )
    # Stage nothing — blob is already in HEAD
    remote_sha = _git(repo, "rev-parse", "origin/main").stdout.strip()
    stdin = f"refs/heads/main {big_sha} refs/heads/main {remote_sha}\n"
    r = _run_prepush(repo, stdin)
    assert r.returncode == 1, f"Hook should block 80MB blob in push range. stderr={r.stderr}"
    assert "BLOCKED" in r.stderr


def test_prepush_ignores_outside_watch(tmp_path):
    """Oversized blob OUTSIDE the watched prefix must not block."""
    repo, _ = _make_repo_with_remote(tmp_path)
    sha = _commit_state_file(repo, "data/big.bin", 80, "outside")
    remote_sha = _git(repo, "rev-parse", "origin/main").stdout.strip()
    stdin = f"refs/heads/main {sha} refs/heads/main {remote_sha}\n"
    r = _run_prepush(repo, stdin)
    assert r.returncode == 0, r.stderr


def test_prepush_handles_new_branch(tmp_path):
    """When remote_sha == ZERO_OID (new branch), hook scans full reachable history."""
    repo, _ = _make_repo_with_remote(tmp_path)
    _git(repo, "checkout", "-q", "-b", "feature")
    big_sha = _commit_state_file(
        repo, ".claude/state/session-signals/cost-tracking.jsonl", 80, "feature"
    )
    stdin = f"refs/heads/feature {big_sha} refs/heads/feature {ZERO_OID}\n"
    r = _run_prepush(repo, stdin)
    assert r.returncode == 1, r.stderr
    assert "BLOCKED" in r.stderr


def test_prepush_branch_deletion_passes(tmp_path):
    """When local_sha == ZERO_OID (delete), nothing to inspect."""
    repo, _ = _make_repo_with_remote(tmp_path)
    remote_sha = _git(repo, "rev-parse", "origin/main").stdout.strip()
    stdin = f"(delete) {ZERO_OID} refs/heads/old {remote_sha}\n"
    r = _run_prepush(repo, stdin)
    assert r.returncode == 0, r.stderr


def test_prepush_threshold_env_override(tmp_path):
    """Allow tuning the threshold without editing the hook."""
    repo, _ = _make_repo_with_remote(tmp_path)
    sha = _commit_state_file(repo, ".claude/state/session-signals/probe.jsonl", 20, "probe")
    remote_sha = _git(repo, "rev-parse", "origin/main").stdout.strip()
    stdin = f"refs/heads/main {sha} refs/heads/main {remote_sha}\n"
    r = _run_prepush(repo, stdin, env_extra={"STATE_SIZE_BLOCK_MB": "10"})
    assert r.returncode == 1
    assert "BLOCKED" in r.stderr
