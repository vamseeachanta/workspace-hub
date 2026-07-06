"""TDD tests for #3384 — scripts/memory/lib/bridge-commit.sh :: bridge_commit_and_push().

The helper is the extracted commit path of bridge-hermes-claude.sh. It must:
  * write a daily, machine-independent heartbeat and COMMIT it (self-stash bug fixed),
  * commit a staged memory change without stranding it in a `pre-bridge-stash`,
  * no-op on a 2nd same-day run and for non-owners,
  * keep the commit pathspec-scoped (unrelated dirt preserved, not swept),
  * push, retrying once through a rebase on a non-fast-forward.

Driven via `bash -c 'source lib; bridge_commit_and_push <repo> <owner> <ts>'` against a temp
git repo + a bare origin (helper takes params, NOT script globals — r1/r2 Finding).
Also asserts the schedule wiring (--commit present + positioned before the log redirect).
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LIB = REPO_ROOT / "scripts" / "memory" / "bridge-commit.sh"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"

MEMORY_FILE = ".claude/memory/agents.md"
CODEX_SLICE = "config/agents/codex/MEMORY.runtime.md"
GEMINI_SLICE = "config/agents/gemini/MEMORY.runtime.md"
HEARTBEAT = ".claude/state/memory-bridge-heartbeat.json"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"git {args} failed: {r.stderr}"
    return r.stdout.strip()


def _seed_repo(tmp_path: Path) -> Path:
    """A working repo tracking the paths the bridge commits, wired to a bare origin on `main`."""
    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q")
    _git(work, "checkout", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    _git(work, "config", "commit.gpgsign", "false")
    for rel in (MEMORY_FILE, CODEX_SLICE, GEMINI_SLICE):
        p = work / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("seed\n")
    (work / ".claude/state").mkdir(parents=True, exist_ok=True)
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "init")
    bare = tmp_path / "origin.git"
    _git(work, "init", "-q", "--bare", str(bare))
    _git(bare, "symbolic-ref", "HEAD", "refs/heads/main")  # so clones check out main, not master
    _git(work, "remote", "add", "origin", str(bare))
    _git(work, "push", "-q", "-u", "origin", "main")
    return work


def _run(repo: Path, owner: str, ts: str = "2026-07-06") -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", f'source "{LIB}"; bridge_commit_and_push "{repo}" "{owner}" "{ts}"'],
        capture_output=True, text=True,
    )


def _count_commits(repo: Path) -> int:
    return int(_git(repo, "rev-list", "--count", "HEAD"))


@pytest.fixture()
def repo(tmp_path):
    if not LIB.exists():
        pytest.skip("bridge-commit.sh not implemented yet")
    return _seed_repo(tmp_path)


# ── heartbeat drives a daily commit even with no content change ───────────────────────────────────
def test_commit_lands_heartbeat_no_content_change(repo):
    before = _count_commits(repo)
    r = _run(repo, "true")
    assert r.returncode == 0, r.stderr
    assert _count_commits(repo) == before + 1
    hb = repo / HEARTBEAT
    assert hb.exists()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert today in hb.read_text()
    # heartbeat is machine-independent (no per-host field) → self-serializing
    assert "machine" not in hb.read_text()
    # and it is actually committed (in HEAD), not just written
    assert HEARTBEAT in _git(repo, "show", "--name-only", "--format=", "HEAD")


def test_second_same_day_run_noops(repo):
    _run(repo, "true")
    after_first = _count_commits(repo)
    r = _run(repo, "true")           # same ts/date → no diff
    assert r.returncode == 0
    assert _count_commits(repo) == after_first


# ── the self-stash bug: a staged content change must be committed, not stashed away ───────────────
def test_commit_lands_staged_change_no_stash(repo):
    (repo / MEMORY_FILE).write_text("NEW CONTENT\n")
    r = _run(repo, "true")
    assert r.returncode == 0, r.stderr
    assert "NEW CONTENT" in _git(repo, "show", f"HEAD:{MEMORY_FILE}")
    assert _git(repo, "stash", "list") == ""          # no pre-bridge-stash left behind


def test_non_owner_no_commit(repo):
    before = _count_commits(repo)
    r = _run(repo, "false")
    assert r.returncode == 0
    assert _count_commits(repo) == before
    assert not (repo / HEARTBEAT).exists()


def test_preserves_unrelated_dirty(repo):
    (repo / MEMORY_FILE).write_text("memory change\n")
    unrelated = repo / "unrelated.txt"
    unrelated.write_text("dirty\n")                    # untracked, unrelated
    r = _run(repo, "true")
    assert r.returncode == 0, r.stderr
    committed = _git(repo, "show", "--name-only", "--format=", "HEAD")
    assert "unrelated.txt" not in committed            # pathspec-scoped: not swept in
    assert unrelated.read_text() == "dirty\n"          # and not lost


def test_push_retry_on_non_ff(repo, tmp_path):
    # advance the bare origin from a second clone → local push is non-FF → helper rebases + retries
    other = tmp_path / "other"
    _git(tmp_path, "clone", "-q", str(tmp_path / "origin.git"), str(other))
    _git(other, "config", "user.email", "o@o")
    _git(other, "config", "user.name", "o")
    _git(other, "config", "commit.gpgsign", "false")
    (other / "someone-else.txt").write_text("x\n")
    _git(other, "add", "-A")
    _git(other, "commit", "-qm", "advance origin")
    _git(other, "push", "-q", "origin", "main")
    # now run the helper on `repo` (its main is behind origin by 1)
    r = _run(repo, "true")
    assert r.returncode == 0, r.stderr
    # the heartbeat commit reached origin (verify from a fresh clone)
    verify = tmp_path / "verify"
    _git(tmp_path, "clone", "-q", str(tmp_path / "origin.git"), str(verify))
    assert (verify / HEARTBEAT).exists()
    assert "someone-else.txt" in _git(verify, "ls-files")   # the other commit preserved


# ── schedule wiring ───────────────────────────────────────────────────────────────────────────────
def _task_command(task_id: str) -> str:
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load(SCHEDULE.read_text())
    for t in data.get("tasks", data if isinstance(data, list) else []):
        if isinstance(t, dict) and t.get("id") == task_id:
            return t["command"]
    # tasks may live under a top-level key; fall back to a scan
    for t in _iter_tasks(data):
        if t.get("id") == task_id:
            return t["command"]
    raise AssertionError(f"task {task_id} not found")


def _iter_tasks(node):
    if isinstance(node, dict):
        if "id" in node and "command" in node:
            yield node
        for v in node.values():
            yield from _iter_tasks(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_tasks(v)


def test_schedule_bridge_commit_flag_position():
    cmd = _task_command("hermes-claude-bridge")
    assert "--commit" in cmd, "Linux bridge must run with --commit"
    # COMMIT_MODE=$1 ⇒ --commit must precede the log redirect, else it lands after >>
    assert cmd.index("--commit") < cmd.index(">>"), "--commit must be before the >> redirect"


def test_schedule_win_stays_dryrun():
    cmd = _task_command("hermes-claude-bridge-win")
    assert "--commit" not in cmd, "Windows bridge intentionally stays dry-run"


def test_heartbeat_path_not_gitignored():
    """The heartbeat MUST be committable in the REAL repo — a `.gitignore` rule that swallows it
    silently defeats the entire liveness clock (its git-commit time is the freshness signal). This
    guards the end-to-end failure the unit tests (temp repos, no .gitignore) could not catch."""
    r = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "check-ignore", HEARTBEAT],
        capture_output=True, text=True,
    )
    assert r.returncode != 0, f"heartbeat path is gitignored (would never commit): {r.stdout.strip()}"
