#!/usr/bin/env python3
"""Dry-run/apply helper for sibling SSoT repairs."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ISSUE_NUMBER = 2775
REPO = "vamseeachanta/workspace-hub"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def require_user_approval(issue_number: int = ISSUE_NUMBER) -> bool:
    """Return True only when live GitHub labels include status:plan-approved; fail closed."""
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_number), "--repo", REPO, "--json", "labels", "--jq", ".labels[].name"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        return False
    return "status:plan-approved" in set(result.stdout.splitlines())


def detect_fs_type(path: Path) -> str:
    try:
        result = run(["findmnt", "-no", "FSTYPE", str(path.resolve(strict=False))], timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip().splitlines()[0] if result.returncode == 0 and result.stdout.strip() else "unknown"


def git_output(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return run(["git", "-C", str(repo), *args], timeout=20)


def is_intxlnk_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and path.read_bytes()[:7] == b"IntxLNK"


def classify_owned_skill_path(path: Path, expected_target: str) -> dict[str, Any]:
    if path.is_symlink():
        target = os.readlink(path)
        return {"status": "ok" if target == expected_target else "rewrite", "kind": "symlink", "target": target}
    if not path.exists():
        return {"status": "rewrite", "kind": "missing"}
    if is_intxlnk_file(path):
        return {"status": "rewrite", "kind": "corrupted_ntfs_symlink"}
    return {"status": "blocked", "kind": "unsafe_owned_path", "path": str(path)}


def capture_owned_paths(paths: list[Path]) -> dict[str, dict[str, Any]]:
    backups: dict[str, dict[str, Any]] = {}
    for path in paths:
        key = str(path)
        if path.is_symlink():
            backups[key] = {"kind": "symlink", "target": os.readlink(path)}
        elif path.exists():
            if path.is_dir():
                backups[key] = {"kind": "directory"}
            else:
                backups[key] = {"kind": "file", "data": path.read_bytes(), "mode": path.stat().st_mode}
        else:
            backups[key] = {"kind": "missing"}
    return backups


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def restore_owned_paths(backups: dict[str, dict[str, Any]]) -> None:
    for raw_path, backup in backups.items():
        path = Path(raw_path)
        remove_path(path)
        kind = backup["kind"]
        if kind == "missing":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "symlink":
            path.symlink_to(backup["target"])
        elif kind == "file":
            path.write_bytes(backup["data"])
            path.chmod(backup["mode"])
        elif kind == "directory":
            path.mkdir(parents=True, exist_ok=True)


def preflight_sibling_repo(repo_path: Path) -> dict[str, Any]:
    fs_type = detect_fs_type(repo_path)
    if fs_type == "ntfs3":
        return {"status": "blocked", "reason": "ntfs3_mount", "path": str(repo_path)}
    if not (repo_path / ".git").exists():
        # Worktrees have .git file, so allow that too.
        if not (repo_path / ".git").is_file():
            return {"status": "blocked", "reason": "not_git_repo", "path": str(repo_path)}
    for path in (repo_path / ".codex" / "skills", repo_path / ".gemini" / "skills"):
        classification = classify_owned_skill_path(path, "__preflight_expected_target_placeholder__")
        if classification["status"] == "blocked":
            return {"status": "blocked", "reason": "unsafe_owned_path", "path": str(path), "kind": classification["kind"]}
    status = git_output(repo_path, ["status", "--porcelain"])
    if status.returncode != 0:
        return {"status": "blocked", "reason": "git_status_failed", "stderr": status.stderr.strip()}
    if status.stdout.strip():
        full_status = git_output(repo_path, ["status", "--porcelain=v1", "--untracked-files=all"])
        status_lines = full_status.stdout.splitlines() if full_status.returncode == 0 else status.stdout.splitlines()
        touched = [line for line in status_lines if any(p in line for p in (".codex/skills", ".gemini/skills", "AGENTS.md"))]
        if touched:
            return {"status": "blocked", "reason": "dirty_touched_paths", "files": touched}
        # Preserve unrelated user/worktree changes; repair owns only provider skill links and AGENTS.md pointers.
        unrelated = status.stdout.splitlines()
    else:
        unrelated = []
    branch = git_output(repo_path, ["symbolic-ref", "--short", "HEAD"])
    if branch.returncode != 0:
        return {"status": "blocked", "reason": "detached_head"}
    if branch.stdout.strip() != "main":
        return {"status": "blocked", "reason": "wrong_branch", "branch": branch.stdout.strip()}
    upstream = git_output(repo_path, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode == 0:
        counts = git_output(repo_path, ["rev-list", "--left-right", "--count", "@{u}...HEAD"])
        if counts.returncode == 0 and counts.stdout.strip():
            behind, ahead = [int(x) for x in counts.stdout.split()[:2]]
            if ahead > 0:
                return {"status": "blocked", "reason": "ahead_of_upstream", "ahead": ahead, "behind": behind}
            if behind > 0:
                return {"status": "blocked", "reason": "behind_upstream", "ahead": ahead, "behind": behind}
    return {"status": "pass", "fs_type": fs_type, "branch": branch.stdout.strip(), "unrelated_dirty_files": unrelated}


def verify_symlink(path: Path, expected_target: str) -> dict[str, Any]:
    if not path.is_symlink():
        return {"status": "fail", "reason": "not_symbolic_link", "path": str(path)}
    target = os.readlink(path)
    if target != expected_target:
        return {"status": "fail", "reason": "wrong_target", "target": target, "expected": expected_target}
    resolved = path.resolve(strict=False)
    if not resolved.exists():
        return {"status": "fail", "reason": "target_missing", "realpath": str(resolved)}
    if not any(resolved.rglob("SKILL.md")):
        return {"status": "fail", "reason": "target_has_no_skill_md", "realpath": str(resolved)}
    file_result = run(["file", "-b", str(path)], timeout=10)
    if file_result.returncode == 0 and "symbolic link" not in file_result.stdout.lower():
        return {"status": "fail", "reason": "file_not_symbolic_link", "file": file_result.stdout.strip()}
    return {"status": "pass", "target": target, "realpath": str(resolved)}


def load_registry() -> dict[str, Any]:
    return yaml.safe_load((repo_root() / "config" / "workstations" / "registry.yaml").read_text()) or {}


def _machine_candidates(name: str, cfg: dict[str, Any]) -> list[str]:
    candidates = [name, str(cfg.get("hostname") or "")]
    candidates += [str(a) for a in (cfg.get("hostname_aliases") or [])]
    return [candidate.split(".")[0].lower() for candidate in candidates if candidate]


def resolve_machine_config(machines: dict[str, Any], machine: str) -> tuple[str, dict[str, Any]]:
    requested = machine.split(".")[0].lower()
    for name, cfg in machines.items():
        if requested in _machine_candidates(name, cfg):
            return name, cfg
    raise SystemExit(f"unknown machine: {machine}")


def _stale_agents_contract_line(text: str) -> bool:
    for line in text.splitlines():
        if re.match(r"^\s*(Contract|Legacy contract):", line) and "../AGENTS.md" in line:
            return True
    return False


def classify_agents_contract(repo_path: Path, tier1_repo_root: Path) -> dict[str, Any]:
    agents = repo_path / "AGENTS.md"
    if agents.is_symlink():
        return {"status": "blocked", "reason": "agents_symlink", "path": str(agents)}
    if not agents.exists():
        return {"status": "blocked", "reason": "missing_agents", "path": str(agents)}
    if not agents.is_file():
        return {"status": "blocked", "reason": "agents_not_regular_file", "path": str(agents)}
    text = agents.read_text(errors="replace")
    if _stale_agents_contract_line(text):
        return {
            "status": "rewrite",
            "kind": "rewrite_agents_pointer",
            "path": str(agents),
            "from": "../AGENTS.md",
            "to": "../workspace-hub/AGENTS.md",
            "reason": "stale_parent_contract",
        }
    if "../AGENTS.md" in text:
        return {
            "status": "blocked",
            "reason": "arbitrary_stale_parent_reference",
            "path": str(agents),
        }
    target = tier1_repo_root / "workspace-hub" / "AGENTS.md"
    contract_re = re.compile(r"^Contract:\s+\.\./workspace-hub/AGENTS\.md(?:\s|\||$)", re.MULTILINE)
    if contract_re.search(text):
        if target.exists():
            return {"status": "ok", "kind": "workspace_hub_contract", "target": str(target)}
        return {
            "status": "blocked",
            "reason": "workspace_hub_contract_target_missing",
            "target": str(target),
            "path": str(agents),
        }
    return {"status": "blocked", "reason": "missing_workspace_hub_contract", "target": str(target), "path": str(agents)}


def build_manifest(machine: str) -> dict[str, Any]:
    machines = load_registry().get("machines") or {}
    machine_name, cfg = resolve_machine_config(machines, machine)
    workspace_root = Path(str(cfg["workspace_root"]))
    tier1 = Path(str(cfg["tier1_repo_root"]))
    repos = []
    for repo in cfg.get("repos") or []:
        repo_path = tier1 / repo
        if not repo_path.exists():
            repos.append({"repo": repo, "status": "not_present", "path": str(repo_path), "actions": []})
            continue
        expected = "../.claude/skills" if repo == "workspace-hub" else "../../workspace-hub/.claude/skills"
        actions = []
        for provider in (".codex", ".gemini"):
            path = repo_path / provider / "skills"
            classification = classify_owned_skill_path(path, expected)
            if classification["status"] == "ok":
                continue
            if classification["status"] == "rewrite":
                actions.append({"kind": "rewrite_symlink", "path": str(path), "target": expected})
            else:
                actions.append({"kind": "blocked", "path": str(path), "reason": classification["kind"]})
        agents = repo_path / "AGENTS.md"
        if repo != "workspace-hub":
            classification = classify_agents_contract(repo_path, tier1)
            if classification["status"] == "rewrite":
                actions.append({key: classification[key] for key in ("kind", "path", "from", "to")})
            elif classification["status"] == "blocked":
                actions.append({"kind": "blocked", **classification})
        repos.append({"repo": repo, "status": "present", "path": str(repo_path), "actions": actions})
    return {"machine": machine_name, "workspace_root": str(workspace_root), "tier1_repo_root": str(tier1), "repos": repos}


def rewrite_agents_pointer(path: Path, old: str, new: str) -> None:
    """Rewrite stale AGENTS contract pointer lines without mutating arbitrary prose."""
    rewritten_lines = []
    for line in path.read_text(errors="replace").splitlines(keepends=True):
        if re.match(r"^\s*(Contract|Legacy contract):", line):
            line = line.replace(old, new)
        rewritten_lines.append(line)
    path.write_text("".join(rewritten_lines))


def apply_manifest(manifest: dict[str, Any]) -> int:
    if not require_user_approval(ISSUE_NUMBER):
        print("blocked: live GitHub status:plan-approved label missing or unavailable", file=sys.stderr)
        return 2
    for repo in manifest["repos"]:
        if not repo["actions"]:
            continue
        repo_path = Path(repo["path"])
        preflight = preflight_sibling_repo(repo_path)
        if preflight["status"] != "pass":
            print(json.dumps({"repo": repo["repo"], "preflight": preflight}, indent=2), file=sys.stderr)
            return 3
        if any(action["kind"] == "blocked" for action in repo["actions"]):
            print(json.dumps({"repo": repo["repo"], "blocked_actions": repo["actions"]}, indent=2), file=sys.stderr)
            return 3
        backups = capture_owned_paths([Path(action["path"]) for action in repo["actions"]])
        try:
            for action in repo["actions"]:
                path = Path(action["path"])
                if action["kind"] == "rewrite_symlink":
                    if path.exists() or path.is_symlink():
                        remove_path(path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(action["target"])
                    verified = verify_symlink(path, action["target"])
                    if verified["status"] != "pass":
                        raise RuntimeError(f"symlink verification failed: {verified}")
                elif action["kind"] == "rewrite_agents_pointer":
                    rewrite_agents_pointer(path, action["from"], action["to"])
                    rewritten_text = path.read_text(errors="replace")
                    if _stale_agents_contract_line(rewritten_text) or action["from"] in rewritten_text:
                        raise RuntimeError(f"AGENTS pointer rewrite verification failed: {path}")
            print(f"applied {repo['repo']}: {len(repo['actions'])} actions")
        except Exception as exc:
            restore_owned_paths(backups)
            print(f"rollback {repo['repo']}: {exc}", file=sys.stderr)
            return 4
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", default="dev-primary")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    manifest = build_manifest(args.machine)
    if args.dry_run or not args.apply:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    return apply_manifest(manifest)


if __name__ == "__main__":
    raise SystemExit(main())
