"""Integration tests for the worktree_guard.py CLI against REAL git (#3143).

Unit tests cover the pure functions with mocked porcelain; this exercises the
live `git worktree list --porcelain` path + exit codes that the bash consumers
(repo-housekeeping.sh etc.) actually gate on.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "lib" / "worktree_guard.py"


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _guard(args, cwd):
    return subprocess.run([sys.executable, str(GUARD), *args], cwd=cwd,
                          capture_output=True, text=True).returncode


def _make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "t@t"], repo)
    _git(["config", "user.name", "t"], repo)
    (repo / "f.txt").write_text("x\n")
    _git(["add", "-A"], repo)
    _git(["commit", "-qm", "init"], repo)
    return repo


def test_cli_refuses_to_delete_checked_out_branch(tmp_path):
    repo = _make_repo(tmp_path)
    wt = tmp_path / "wt-feature"
    _git(["worktree", "add", "-q", "-b", "feat/active", str(wt)], repo)
    # checked out in a live worktree -> exit 1 (refused)
    assert _guard(["safe-delete-branch", "feat/active"], repo) == 1
    # a branch not checked out anywhere -> exit 0 (allowed)
    assert _guard(["safe-delete-branch", "feat/not-checked-out"], repo) == 0


def test_cli_remove_worktree_deny_by_default_then_mark_owner(tmp_path):
    repo = _make_repo(tmp_path)
    wt = tmp_path / "wt-owned"
    _git(["worktree", "add", "-q", "-b", "feat/owned", str(wt)], repo)
    # unowned -> refused (exit 1)
    assert _guard(["safe-remove-worktree", str(wt), "housekeeping"], repo) == 1
    # mark ownership, then allowed (exit 0)
    assert _guard(["mark-owner", str(wt), "housekeeping"], repo) == 0
    assert (wt / ".wt-owner").read_text().strip() == "housekeeping"
    assert _guard(["safe-remove-worktree", str(wt), "housekeeping"], repo) == 0
    # a different owner is still refused
    assert _guard(["safe-remove-worktree", str(wt), "overnight-dispatch"], repo) == 1
    # is-owned mirrors ownership (used to gate the foreign-WIP-commit loop)
    assert _guard(["is-owned", str(wt), "housekeeping"], repo) == 0
    assert _guard(["is-owned", str(wt), "overnight-dispatch"], repo) == 1
