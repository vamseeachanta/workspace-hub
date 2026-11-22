#!/usr/bin/env python3
"""Portable, single-repository sync with explicit upstreams and no auto-commit.

Git command contracts: git-status(1), git-rev-list(1), git-fetch(1), git-merge(1),
git-push(1), and git-for-each-ref(1); see the worked example documentation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Tool names are the baseline in issue 3880, not inferred version requirements.
TOOLS = ("git", "gh", "node", "python3", "claude", "codex")
PROTECTED = frozenset({"main", "master"})
# Repository selectors must not redirect an explicit --repo to another checkout.
GIT_BINDINGS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX", "GIT_CEILING_DIRECTORIES",
)


class SyncError(Exception):
    """A prerequisite or Git operation failed; no recovery is performed."""


def git(repo: Path, *args: str, optional: bool = False) -> str | None:
    """Run argument-vector Git; suppress raw output that may contain credentials."""
    env = os.environ.copy()
    for key in GIT_BINDINGS:
        env.pop(key, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], env=env,
            text=True, capture_output=True, check=False,
        )
    except OSError as error:
        raise SyncError("Git could not start; check the installation and repository.") from error
    if result.returncode:
        if optional:
            return None
        raise SyncError(
            f"Git {args[0]} failed (exit {result.returncode}); "
            "inspect the selected repository locally."
        )
    return result.stdout.strip()


def status(repo: Path) -> dict:
    """Report local tracking state; status never contacts a remote."""
    if git(repo, "rev-parse", "--is-inside-work-tree") != "true":
        raise SyncError("Select a repository working tree.")
    branch = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", optional=True)
    upstream = git(repo, "rev-parse", "--verify", "@{upstream}", optional=True)
    ahead = behind = None
    if upstream:
        counts = git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
        ahead, behind = map(int, counts.split())
    return {
        "branch": branch,
        "dirty": bool(git(repo, "status", "--porcelain=v1", "--untracked-files=normal")),
        "has_upstream": upstream is not None,
        "ahead": ahead,
        "behind": behind,
        "comparison": "local-tracking-ref",
    }


def doctor() -> dict:
    """Inspect executable presence without starting assistants or installing tools."""
    tools = {name: "present" if shutil.which(name) else "missing" for name in TOOLS}
    return {
        "tools": tools,
        "ready": all(value == "present" for value in tools.values()),
        "versions": "not-evaluated",
    }


def check_operation(repo: Path) -> None:
    """Refuse synchronization during unfinished Git operations."""
    for marker in (
        "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply",
    ):
        marker_path = Path(git(repo, "rev-parse", "--git-path", marker))
        if not marker_path.is_absolute():
            marker_path = repo / marker_path
        if marker_path.exists():
            raise SyncError("An unfinished Git operation requires local resolution.")


def sync(repo: Path, command: str) -> dict:
    """Pull by fast-forward or push only HEAD to its configured upstream branch."""
    if command not in {"pull", "push"}:
        raise SyncError("Unknown synchronization command.")
    state = status(repo)
    if state["branch"] is None:
        raise SyncError("A detached HEAD cannot be synchronized.")
    if state["dirty"]:
        raise SyncError("Review and commit uncommitted changes before synchronization.")
    if not state["has_upstream"]:
        raise SyncError("An existing upstream branch is required.")
    check_operation(repo)
    target = git(
        repo, "for-each-ref", "--format=%(upstream:remotename)%09%(upstream:remoteref)",
        "--", f"refs/heads/{state['branch']}",
    )
    fields = target.split("\t")
    if len(fields) != 2 or not fields[0] or not fields[1].startswith("refs/heads/"):
        raise SyncError("A configured remote upstream branch is required.")
    remote, ref = fields
    if remote == ".":
        raise SyncError("A remote upstream is required; a local branch is insufficient.")
    if command == "push":
        if state["branch"] in PROTECTED or ref.removeprefix("refs/heads/") in PROTECTED:
            raise SyncError("Push to or from a protected branch is refused.")
        git(repo, "push", "--porcelain", "--no-follow-tags", "--recurse-submodules=no",
            "--", remote, f"HEAD:{ref}")
    else:
        git(repo, "fetch", "--no-recurse-submodules", "--", remote, ref)
        git(repo, "-c", "submodule.recurse=false", "merge", "--ff-only",
            "--no-overwrite-ignore", "--no-edit", "FETCH_HEAD")
    return {"operation": command, "result": "completed"}


def inventory(root: Path, expected: list[str]) -> dict:
    """Inspect immediate nonhidden folders against a caller-supplied repo set."""
    if any(not name or name in {".", ".."} or "/" in name or "\\" in name
           for name in expected):
        raise SyncError("Expected repositories must be single folder names.")
    repositories, unmanaged, unverified, links = [], [], [], []
    try:
        entries = sorted(root.iterdir())
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.is_symlink():
                links.append(entry.name)
            elif entry.is_dir():
                if not (entry / ".git").exists():
                    unmanaged.append(entry.name)
                    continue
                try:
                    top = git(entry, "rev-parse", "--show-toplevel")
                    if Path(top).resolve() != entry.resolve():
                        raise SyncError("Repository root mismatch.")
                    repositories.append(entry.name)
                except SyncError:
                    unverified.append(entry.name)
    except OSError as error:
        raise SyncError("Workspace root could not be inspected.") from error
    missing = sorted(set(expected) - set(repositories))
    unexpected = sorted(set(repositories) - set(expected)) if expected else []
    return {
        "repositories": repositories,
        "unmanaged": unmanaged,
        "unverified": unverified,
        "excluded_links": links,
        "missing": missing,
        "unexpected": unexpected,
        "criterion": "explicit-folder-set" if expected else "not-supplied",
        "ready": not (missing or unexpected or unverified) if expected else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "pull", "push", "doctor", "inventory"))
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                        help="Selected working tree or a directory inside it (default: cwd)")
    parser.add_argument("--root", type=Path, help="Workspace root for inventory only")
    parser.add_argument("--expect", nargs="+", default=[], help="Expected repository folder names")
    args = parser.parse_args(argv)
    if args.command == "inventory" and args.root is None:
        parser.error("inventory requires --root")
    if args.command != "inventory" and (args.root is not None or args.expect):
        parser.error("--root and --expect apply only to inventory")
    try:
        if args.command == "doctor":
            report = doctor()
        elif args.command == "inventory":
            report = inventory(args.root, args.expect)
        elif args.command == "status":
            report = status(args.repo)
        else:
            report = sync(args.repo, args.command)
        print(json.dumps(report, sort_keys=True))
        if args.command in {"doctor", "inventory"}:
            return int(report["ready"] is False)
        return 0
    except SyncError as error:
        print(f"ws: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
