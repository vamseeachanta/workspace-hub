#!/usr/bin/env python3
"""Read-only repo-sync cleanup audit primitives.

This ports the deterministic parts of the local repo-sync-cleanup-audit routine
into workspace-hub without touching the live timer or prompt.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def run_git(repo: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=check,
    )


def finding(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def is_git_repo(path: Path) -> bool:
    try:
        result = run_git(path, "rev-parse", "--is-inside-work-tree")
    except OSError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def current_branch(repo: Path) -> str:
    result = run_git(repo, "branch", "--show-current")
    return result.stdout.strip() if result.returncode == 0 else ""


def default_ref(repo: Path) -> str:
    result = run_git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    for ref in ("origin/main", "origin/master", "main", "master"):
        result = run_git(repo, "rev-parse", "--verify", ref)
        if result.returncode == 0:
            return ref
    return ""


def has_common_ancestor(repo: Path, left: str, right: str) -> bool:
    result = run_git(repo, "merge-base", left, right)
    return result.returncode == 0 and bool(result.stdout.strip())


def unique_commit_count(repo: Path, base_ref: str) -> int | None:
    if not base_ref:
        return None
    if not has_common_ancestor(repo, "HEAD", base_ref):
        return None
    result = run_git(repo, "rev-list", "--count", f"{base_ref}..HEAD")
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def same_name_remote_branches(repo: Path, branch: str) -> list[str]:
    if not branch:
        return []
    result = run_git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/remotes",
    )
    if result.returncode != 0:
        return []
    matches: list[str] = []
    for line in result.stdout.splitlines():
        ref = line.strip()
        if "/" not in ref:
            continue
        _, remote_branch = ref.split("/", 1)
        if remote_branch == branch:
            matches.append(ref)
    return sorted(matches)


def remote_contains_head(repo: Path, remote_branch: str) -> bool:
    result = run_git(repo, "merge-base", "--is-ancestor", "HEAD", remote_branch)
    return result.returncode == 0


def working_tree_counts(repo: Path) -> tuple[int, int]:
    result = run_git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    tracked_missing = 0
    modified = 0
    if result.returncode != 0:
        return (0, 0)
    for raw in result.stdout.splitlines():
        if not raw:
            continue
        xy = raw[:2]
        if "D" in xy:
            tracked_missing += 1
        elif xy.strip() and not xy.startswith("??"):
            modified += 1
    return tracked_missing, modified


def nested_full_clones(path: Path) -> list[Path]:
    nested: list[Path] = []
    for git_dir in path.rglob(".git"):
        if is_known_cache_path(path, git_dir):
            continue
        if git_dir.parent == path:
            continue
        if git_dir.is_file() and is_submodule_gitfile(path, git_dir):
            continue
        if git_dir.is_dir() or git_dir.is_file():
            nested.append(git_dir.parent)
    return sorted(nested)


def is_known_cache_path(parent: Path, candidate: Path) -> bool:
    cache_root = (parent / ".claude" / "state" / "uv-cache").resolve()
    try:
        resolved = candidate.resolve()
    except OSError:
        return False
    return resolved == cache_root or cache_root in resolved.parents


def is_submodule_gitfile(parent: Path, git_file: Path) -> bool:
    prefix = "gitdir:"
    try:
        content = git_file.read_text().strip()
    except OSError:
        return False
    if not content.startswith(prefix):
        return False
    target = Path(content.removeprefix(prefix).strip())
    if not target.is_absolute():
        target = (git_file.parent / target).resolve()
    parent_modules = (parent / ".git" / "modules").resolve()
    return target == parent_modules or parent_modules in target.parents


def audit_path(path: Path | str, *, public_parent: bool = False) -> dict[str, Any]:
    repo = Path(path).resolve()
    findings: list[dict[str, str]] = []
    if not repo.exists() or not is_git_repo(repo):
        return {
            "path": str(repo),
            "status": "NOT-A-REPO",
            "findings": [finding("NOT-A-REPO", "INFO", "directory is not a Git worktree")],
        }

    branch = current_branch(repo)
    base_ref = default_ref(repo)
    unique_count = unique_commit_count(repo, base_ref)
    same_name_remotes = same_name_remote_branches(repo, branch)
    tracked_missing, modified = working_tree_counts(repo)
    nested = nested_full_clones(repo)

    if base_ref and unique_count is None:
        findings.append(finding("UNRELATED-HISTORY", "WARN", f"HEAD has no common ancestor with {base_ref}"))
    elif unique_count:
        pushed_to_same_name = any(remote_contains_head(repo, remote) for remote in same_name_remotes)
        if not pushed_to_same_name:
            findings.append(finding("UNPUSHED", "WARN", f"{unique_count} commits are not on a same-name remote branch"))

    if tracked_missing:
        findings.append(finding("TRACKED-MISSING", "WARN", f"{tracked_missing} tracked files are missing"))
    if modified:
        findings.append(finding("MODIFIED", "WARN", f"{modified} tracked files are modified"))
    for nested_repo in nested:
        message = "nested full clone inside worktree"
        if public_parent:
            message = f"private repo inside public worktree: {nested_repo.relative_to(repo)}"
        findings.append(finding("PRIVACY-NESTED-CLONE", "WARN", message))

    return {
        "path": str(repo),
        "status": "WARN" if findings else "OK",
        "branch": branch,
        "default_ref": base_ref,
        "unique_commit_count": unique_count,
        "same_name_remote_branches": same_name_remotes,
        "tracked_missing_count": tracked_missing,
        "modified_count": modified,
        "nested_clone_count": len(nested),
        "nested_clones": [str(item) for item in nested],
        "findings": findings,
    }


def audit_root(root: Path, *, public_parent_names: set[str] | None = None) -> list[dict[str, Any]]:
    names = public_parent_names or set()
    rows = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_dir():
            continue
        rows.append(audit_path(entry, public_parent=entry.name in names))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Repository or ecosystem root to audit")
    parser.add_argument("--root", action="store_true", help="Audit each child directory under path")
    parser.add_argument("--public-parent", action="append", default=[], help="Child name treated as public")
    args = parser.parse_args()

    if args.root:
        payload: Any = audit_root(args.path, public_parent_names=set(args.public_parent))
    else:
        payload = audit_path(args.path, public_parent=bool(args.public_parent))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
