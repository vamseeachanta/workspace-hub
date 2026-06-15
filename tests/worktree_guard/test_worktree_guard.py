"""Tests for scripts/lib/worktree_guard.py (#3143).

Deny-by-default ownership guard so cleanup/dispatch automation never destroys a
worktree it didn't create or deletes a branch checked out in a live worktree.

Pure functions + a tmp-dir marker check — fully offline (no real git state).
Module loaded by file path via importlib (mirrors tests/ai/test_provider_route.py).
NOTE: lives under tests/worktree_guard/ not tests/lib/ — `.gitignore:42 lib/` would
untrack the latter.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "lib" / "worktree_guard.py"
spec = importlib.util.spec_from_file_location("worktree_guard", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["worktree_guard"] = module
spec.loader.exec_module(module)

parse_worktree_branches = module.parse_worktree_branches
branch_is_checked_out = module.branch_is_checked_out
worktree_is_owned = module.worktree_is_owned
safe_to_remove_worktree = module.safe_to_remove_worktree
safe_to_delete_branch = module.safe_to_delete_branch
OWNER_MARKER = module.OWNER_MARKER

PORCELAIN = """\
worktree /mnt/local-analysis/workspace-hub
HEAD aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
branch refs/heads/main

worktree /tmp/wt-feature
HEAD bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
branch refs/heads/feat/g1-portable-agent-def

worktree /tmp/wt-detached
HEAD cccccccccccccccccccccccccccccccccccccccc
detached
"""


# --- pure parsing -----------------------------------------------------------

def test_parse_worktree_branches():
    m = parse_worktree_branches(PORCELAIN)
    assert m["/mnt/local-analysis/workspace-hub"] == "main"
    assert m["/tmp/wt-feature"] == "feat/g1-portable-agent-def"
    assert m["/tmp/wt-detached"] is None  # detached HEAD -> no branch


def test_branch_is_checked_out():
    assert branch_is_checked_out("feat/g1-portable-agent-def", PORCELAIN) is True
    assert branch_is_checked_out("main", PORCELAIN) is True
    assert branch_is_checked_out("some/other-branch", PORCELAIN) is False


# --- ownership (deny-by-default) --------------------------------------------

def test_worktree_owned_only_when_marker_matches(tmp_path):
    (tmp_path / OWNER_MARKER).write_text("housekeeping\n")
    assert worktree_is_owned(tmp_path, "housekeeping") is True
    assert worktree_is_owned(tmp_path, "overnight-dispatch") is False  # different owner


def test_unowned_worktree_is_not_owned(tmp_path):
    # no marker file at all
    assert worktree_is_owned(tmp_path, "housekeeping") is False


def test_safe_to_remove_is_deny_by_default(tmp_path):
    # An UNOWNED (foreign / active-session) worktree must NEVER be removable.
    assert safe_to_remove_worktree(tmp_path, "housekeeping") is False
    # Only a worktree this job owns is removable.
    (tmp_path / OWNER_MARKER).write_text("housekeeping\n")
    assert safe_to_remove_worktree(tmp_path, "housekeeping") is True
    # Owned by someone else -> still refused.
    assert safe_to_remove_worktree(tmp_path, "overnight-dispatch") is False


# --- branch deletion guard --------------------------------------------------

def test_branch_checked_out_is_not_safe_to_delete():
    # The incident shape: branch was pushed (so "unpushed" guard fails) but is
    # still checked out in a live worktree -> must be refused.
    assert safe_to_delete_branch("feat/g1-portable-agent-def", PORCELAIN) is False


def test_unreferenced_branch_is_safe_to_delete():
    assert safe_to_delete_branch("some/merged-branch", PORCELAIN) is True
