#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Deny-by-default worktree/branch ownership guard (#3143).

Cleanup and dispatch automation (repo-housekeeping.sh, daily-cleanup.sh, overnight
dispatch) has destroyed ACTIVE session worktrees and force-deleted branches with
unpushed-or-pushed work. This guard makes destruction opt-IN by ownership rather
than opt-OUT by naming:

  - A job may remove ONLY a worktree it created, proven by a `.wt-owner` marker
    file it wrote containing its owner tag. An unowned / foreign / active-session
    worktree is NEVER removable (deny-by-default).
  - A branch checked out in ANY live worktree is NEVER deletable — this is the
    load-bearing guard (the incident branch was already PUSHED, so an
    "unpushed?" check would not have protected it; "checked out?" would).

Pure functions are unit-tested offline; the CLI lets bash consumers gate actions:

  python worktree_guard.py safe-delete-branch <branch>      # exit 0 = safe
  python worktree_guard.py safe-remove-worktree <dir> <owner>
  python worktree_guard.py mark-owner <dir> <owner>         # write the marker
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

OWNER_MARKER = ".wt-owner"


def parse_worktree_branches(porcelain: str) -> dict[str, str | None]:
    """Map worktree path -> short branch name (None for detached HEAD).

    Input is `git worktree list --porcelain` output.
    """
    result: dict[str, str | None] = {}
    path: str | None = None
    for line in porcelain.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):].strip()
            result[path] = None  # default until a branch line is seen
        elif line.startswith("branch ") and path is not None:
            ref = line[len("branch "):].strip()
            result[path] = ref.removeprefix("refs/heads/")
        elif line == "" :
            path = None
    return result


def branch_is_checked_out(branch: str, porcelain: str) -> bool:
    """True if `branch` is checked out in ANY worktree."""
    return branch in (b for b in parse_worktree_branches(porcelain).values() if b)


def worktree_is_owned(worktree_dir: Path | str, owner: str) -> bool:
    """True only if `worktree_dir` carries a .wt-owner marker matching `owner`."""
    marker = Path(worktree_dir) / OWNER_MARKER
    if not marker.is_file():
        return False
    return marker.read_text(encoding="utf-8").strip() == owner.strip()


def safe_to_remove_worktree(worktree_dir: Path | str, owner: str) -> bool:
    """Deny-by-default: a worktree is removable ONLY if `owner` owns it."""
    return worktree_is_owned(worktree_dir, owner)


def safe_to_delete_branch(branch: str, porcelain: str) -> bool:
    """A branch checked out in any live worktree must NOT be deleted."""
    return not branch_is_checked_out(branch, porcelain)


# --- thin CLI for bash consumers -------------------------------------------

def _live_porcelain() -> str:
    return subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True,
    ).stdout


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: worktree_guard.py {safe-delete-branch|safe-remove-worktree|mark-owner} ...",
              file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "safe-delete-branch":
        branch = rest[0]
        return 0 if safe_to_delete_branch(branch, _live_porcelain()) else 1
    if cmd == "safe-remove-worktree":
        wt, owner = rest[0], rest[1]
        return 0 if safe_to_remove_worktree(wt, owner) else 1
    if cmd == "mark-owner":
        wt, owner = rest[0], rest[1]
        (Path(wt) / OWNER_MARKER).write_text(owner.strip() + "\n", encoding="utf-8")
        return 0
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
