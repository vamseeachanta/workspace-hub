#!/usr/bin/env python3
"""Read-only workspace-root layout & _wt/ purity auditor.

Checks a workstation's canonical workspace root (e.g. ~/ws or C:/ws) against
config/workstations/ws-root-policy.yaml without modifying any files.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
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
    return data


def _matches_any(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def _check_linked_worktree(entry: Path) -> tuple[bool, str]:
    git_marker = entry / ".git"
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
    gitdir_path = Path(gitdir_str)
    if not gitdir_path.is_absolute():
        gitdir_path = (entry / gitdir_path).resolve()
    if not gitdir_path.exists():
        return False, "broken_worktree_gitdir"
    return True, "ok"


def audit_workspace_root(
    root: Path,
    policy: dict[str, Any],
    allow_extra_dirs: list[str] | None = None,
) -> dict[str, Any]:
    """Audit a workspace root directory against ws-root-policy.yaml."""
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Workspace root does not exist or is not a dir: {root}")

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

    for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        name = entry.name
        if entry.is_symlink():
            violations.append({
                "scope": "root",
                "name": name,
                "kind": "symlink_at_root",
                "reason": "Symlinks/junctions should not sit inside workspace root",
            })
            continue

        if entry.is_file():
            if not allow_loose_files:
                violations.append({
                    "scope": "root",
                    "name": name,
                    "kind": "loose_root_file",
                    "reason": "Loose files belong inside a destined repository or _pm/scripts",
                })
            continue

        # Directory entry
        if name in reserved or name in allowed_dotdirs or name in extra_allowed:
            reserved_present.append(name)
            continue

        if _matches_any(name, forbidden_patterns):
            violations.append({
                "scope": "root",
                "name": name,
                "kind": "forbidden_root_pattern",
                "reason": "Matches forbidden root clutter pattern in ws-root-policy.yaml",
            })
            continue

        git_path = entry / ".git"
        if git_path.is_dir():
            git_repos.append(name)
        elif git_path.is_file():
            violations.append({
                "scope": "root",
                "name": name,
                "kind": "worktree_at_root",
                "reason": "Linked worktrees must live under _wt/, not at workspace root",
            })
        else:
            violations.append({
                "scope": "root",
                "name": name,
                "kind": "non_git_root_dir",
                "reason": "Unprefixed root directories must be git repositories (.git/)",
            })

    # Audit _wt/ purity if present
    wt_dir = root / "_wt"
    if wt_dir.is_dir() and not wt_dir.is_symlink():
        for child in sorted(wt_dir.iterdir(), key=lambda p: p.name.lower()):
            if child.is_file():
                wt_summary["violations"].append({
                    "scope": "_wt",
                    "name": child.name,
                    "kind": "loose_file_in_wt",
                    "reason": "_wt/ holds linked git worktrees only; move scratch to $TEMP or _scratch/",
                })
                continue
            ok, reason = _check_linked_worktree(child)
            if ok:
                wt_summary["linked_worktrees"].append(child.name)
            else:
                wt_summary["violations"].append({
                    "scope": "_wt",
                    "name": child.name,
                    "kind": reason,
                    "reason": "Non-worktree or broken entry inside _wt/",
                })

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
        f"# Workspace Root Hygiene Audit — {status}",
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
