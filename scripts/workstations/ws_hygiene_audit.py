#!/usr/bin/env python3
"""Read-only workspace-root layout & _wt/ purity auditor.

Checks a workstation's registered work root against
config/workstations/ws-root-policy.yaml without modifying any files.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "workstations"
    / "ws-root-policy.yaml"
)


def load_policy(policy_path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    with policy_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Policy file {policy_path} did not parse to a mapping")
    repositories = data.get("registered_repositories")
    if not isinstance(repositories, list) or not all(isinstance(name, str) for name in repositories):
        raise ValueError("Policy must list registered_repositories")
    if registry_name := data.get("workstation_registry"):
        with (policy_path.parent / registry_name).open(encoding="utf-8") as fh:
            machines = yaml.safe_load(fh)["machines"]
        registered = {name for machine in machines.values() for name in machine["repos"]}
        data["registered_repositories"] = sorted(registered.union(repositories))
    return data


def _matches_any(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def _is_directory_link(entry: Path) -> bool:
    if entry.is_symlink():
        return True
    try:
        attributes = getattr(entry.lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _check_linked_worktree(entry: Path) -> tuple[bool, str]:
    git_marker = entry / ".git"
    if _is_directory_link(git_marker):
        return False, "symlinked_git_marker"
    if git_marker.is_dir():
        return False, "standalone_clone_in_wt"
    if not git_marker.is_file():
        return False, "non_git_dir_in_wt"
    try:
        raw = git_marker.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as exc:
        return False, f"unreadable_git_file:{exc}"
    if not raw.lower().startswith("gitdir:"):
        return False, "malformed_git_file"
    gitdir_str = raw.split(":", 1)[1].strip()
    if "\x00" in gitdir_str:
        return False, "malformed_git_file"
    gitdir_path = Path(gitdir_str)
    if not gitdir_path.is_absolute():
        gitdir_path = (entry / gitdir_path).resolve()
    if not gitdir_path.is_dir():
        return False, "broken_worktree_gitdir"

    commondir_file = gitdir_path / "commondir"
    backlink_file = gitdir_path / "gitdir"
    head_file = gitdir_path / "HEAD"
    if not commondir_file.is_file():
        return False, "not_linked_worktree_gitdir"
    try:
        commondir_raw = commondir_file.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as exc:
        return False, f"unreadable_commondir:{exc}"
    if not commondir_raw:
        return False, "not_linked_worktree_gitdir"
    commondir_path = Path(commondir_raw)
    if not commondir_path.is_absolute():
        commondir_path = (gitdir_path / commondir_path).resolve()
    if not commondir_path.is_dir():
        return False, "broken_worktree_commondir"

    if not head_file.is_file():
        return False, "incomplete_worktree_metadata"

    if not backlink_file.is_file():
        return False, "invalid_worktree_backlink"
    try:
        backlink_raw = backlink_file.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as exc:
        return False, f"unreadable_backlink:{exc}"
    if not backlink_raw:
        return False, "invalid_worktree_backlink"
    backlink_path = Path(backlink_raw)
    if not backlink_path.is_absolute():
        backlink_path = (gitdir_path / backlink_path).resolve()
    try:
        if not os.path.samefile(backlink_path, git_marker):
            return False, "invalid_worktree_backlink"
    except OSError:
        return False, "invalid_worktree_backlink"

    return _verify_git_marker(entry, commondir_path)


def _verify_git_marker(entry: Path, common_dir: Path | None = None) -> tuple[bool, str]:
    # Resolve this exact marker so Git cannot discover a parent repository.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        def run_git(*args: str) -> subprocess.CompletedProcess[bytes]:
            return subprocess.run(
                ["git", *args],
                cwd=entry, env=env, capture_output=True, timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

        if run_git("rev-parse", "--resolve-git-dir", ".git").returncode:
            return False, "incomplete_worktree_metadata" if common_dir else "invalid_git_marker"
        if common_dir is not None:
            listing = run_git("--git-dir", str(common_dir), "worktree", "list", "--porcelain", "-z")
            if listing.returncode:
                return False, "git_verification_unavailable"
            checkout = entry.resolve()
            paths = (os.fsdecode(field[len(b"worktree "):]) for field in listing.stdout.split(b"\0")
                     if field.startswith(b"worktree "))
            if not any(Path(path) == checkout for path in paths):
                return False, "unregistered_worktree"
    except subprocess.TimeoutExpired:
        return False, "git_verification_timeout"
    except OSError:
        return False, "git_verification_unavailable"
    return True, "ok"


def _permission_finding(path: Path, scope: str) -> dict[str, str]:
    return {"scope": scope, "name": path.name, "kind": "permission_denied",
            "reason": "Access denied during inspection"}


def _inspect_children(directory: Path, scope: str, inspect: Callable[[Path], None],
                      findings: list[dict[str, str]]) -> None:
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except PermissionError:
        findings.append(_permission_finding(directory, scope))
        return
    for entry in entries:
        try:
            inspect(entry)
        except PermissionError:
            findings.append(_permission_finding(entry, scope))


def audit_workspace_root(
    root: Path,
    policy: dict[str, Any],
    allow_extra_dirs: list[str] | None = None,
) -> dict[str, Any]:
    """Audit a workspace root directory against ws-root-policy.yaml."""
    registered = set(policy["registered_repositories"])
    reserved = set((policy.get("reserved_system_dirs") or {}).keys())
    allowed_dotdirs = set(policy.get("allowed_tool_dotdirs") or [])
    extra_allowed = set(allow_extra_dirs or [])
    forbidden_patterns = list(policy.get("forbidden_root_patterns") or [])
    allow_loose_files = bool((policy.get("root_rules") or {}).get("allow_loose_files", False))

    git_repos: list[str] = []
    reserved_present: list[str] = []
    violations: list[dict[str, str]] = []
    wt_summary: dict[str, Any] = {
        "linked_worktrees": [],
        "violations": [],
    }

    def inspect_root(entry: Path) -> None:
        name = entry.name
        if _is_directory_link(entry):
            kind, reason = "symlink_at_root", "Symlink or junction inside the work root"
        elif _matches_any(name, forbidden_patterns):
            kind, reason = "forbidden_root_pattern", "Matches a forbidden root clutter pattern"
        elif name in reserved and not entry.is_dir():
            kind, reason = "invalid_reserved_directory", "Reserved entry must be a directory"
        elif entry.is_file():
            if allow_loose_files:
                return
            kind, reason = "loose_root_file", "Loose files belong inside a repository or _pm/scripts"
        elif name in reserved or name in allowed_dotdirs:
            reserved_present.append(name)
            return
        else:
            marker = entry / ".git"
            if _is_directory_link(marker):
                kind, reason = "symlinked_git_marker", "Repository marker is a symlink or reparse point"
            elif marker.is_dir():
                if name in registered:
                    ok, kind = _verify_git_marker(entry)
                    if ok:
                        git_repos.append(name)
                        return
                    reason = "Git could not verify the repository marker"
                else:
                    kind, reason = "unregistered_repository", "Repository is absent from the policy registry"
            elif marker.is_file():
                kind, reason = "worktree_at_root", "Linked worktrees belong under _wt/"
            elif name in extra_allowed:
                reserved_present.append(name)
                return
            else:
                kind, reason = "non_git_root_dir", "Root directory has no .git/ directory"
        violations.append({"scope": "root", "name": name, "kind": kind, "reason": reason})

    def inspect_worktree(child: Path) -> None:
        if _is_directory_link(child):
            kind, reason = "symlink_in_wt", "Symlink or junction inside _wt/"
        elif child.is_file():
            kind = "loose_file_in_wt"
            reason = "_wt/ holds linked git worktrees only; move scratch to $TEMP or the repository's .tmp/"
        else:
            ok, kind = _check_linked_worktree(child)
            if ok:
                short, _, slug = child.name.partition("--")
                if short and slug:
                    wt_summary["linked_worktrees"].append(child.name)
                    return
                kind, reason = "invalid_worktree_name", "Expected <repo-short>--<slug>"
            else:
                reason = "Non-worktree or broken entry inside _wt/"
        wt_summary["violations"].append({"scope": "_wt", "name": child.name, "kind": kind, "reason": reason})

    try:
        if _is_directory_link(root):
            violations.append({"scope": "root", "name": root.name, "kind": "workspace_root_alias",
                               "reason": "Audit the registered work root directly"})
        elif not root.is_dir():
            raise FileNotFoundError(f"Workspace root does not exist or is not a dir: {root}")
        else:
            _inspect_children(root, "root", inspect_root, violations)
    except PermissionError:
        violations.append(_permission_finding(root, "root"))

    if "_wt" in reserved_present:
        _inspect_children(root / "_wt", "_wt", inspect_worktree, wt_summary["violations"])

    all_violations = violations + wt_summary["violations"]
    return {
        "root": str(root),
        "compliant": len(all_violations) == 0,
        "git_repo_count": len(git_repos),
        "git_repos": git_repos,
        "reserved_dirs_present": reserved_present,
        "root_violation_count": len(violations),
        "root_violations": violations,
        "wt_linked_count": len(wt_summary["linked_worktrees"]),
        "wt_violation_count": len(wt_summary["violations"]),
        "wt_violations": wt_summary["violations"],
        "total_violations": len(all_violations),
    }


def format_markdown(report: dict[str, Any]) -> str:
    status = "COMPLIANT" if report["compliant"] else f"NON-COMPLIANT ({report['total_violations']} violations)"
    lines = [
        f"# Workspace Root Hygiene Audit â€” {status}",
        "",
        f"- **Git repositories:** {report['git_repo_count']}",
        f"- **Reserved system dirs:** {', '.join(report['reserved_dirs_present']) or 'none'}",
        f"- **Linked worktrees in `_wt/`:** {report['wt_linked_count']}",
        f"- **Root violations:** {report['root_violation_count']}",
        f"- **`_wt/` violations:** {report['wt_violation_count']}",
    ]
    if report["root_violations"]:
        lines.extend(["", "## Root Violations", "| Name | Kind | Reason |", "| :--- | :--- | :--- |"])
        for v in report["root_violations"]:
            lines.append(f"| `{v['name']}` | `{v['kind']}` | {v['reason']} |")
    if report["wt_violations"]:
        lines.extend(["", "## `_wt/` Violations", "| Name | Kind | Reason |", "| :--- | :--- | :--- |"])
        for v in report["wt_violations"]:
            lines.append(f"| `{v['name']}` | `{v['kind']}` | {v['reason']} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit workspace root against ws-root-policy.yaml")
    parser.add_argument("--root", type=Path, required=True, help="Workspace root directory to audit")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH, help="Path to ws-root-policy.yaml")
    parser.add_argument(
        "--allow-extra-dir",
        action="append",
        default=[],
        help="Host-specific runtime directory to allowlist (repeatable)",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any violation is found")
    args = parser.parse_args(argv)

    policy = load_policy(args.policy)
    report = audit_workspace_root(args.root, policy, allow_extra_dirs=args.allow_extra_dir)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_markdown(report))
    if args.strict and not report["compliant"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
