#!/usr/bin/env python3
"""Check workspace-hub single-source-of-truth flow across sibling repos."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

VALID_STATUSES = {"pass", "fail", "not_present"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def has_skill_md(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    return any(path.rglob("SKILL.md"))


def _section(status: str = "not_present", **extra: Any) -> dict[str, Any]:
    assert status in VALID_STATUSES
    section = {"status": status, "evidence_paths": []}
    section.update(extra)
    return section


def empty_report() -> dict[str, dict[str, Any]]:
    return {
        "memory": _section(),
        "skills": _section(),
        "harness_contracts": _section(),
        "registry": _section(),
    }


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return yaml.safe_load(fh) or {}


def _machine_candidates(name: str, cfg: dict[str, Any]) -> list[str]:
    candidates = [name, str(cfg.get("hostname") or "")]
    candidates += [str(a) for a in (cfg.get("hostname_aliases") or [])]
    return [c.split(".")[0].lower() for c in candidates if c]


def resolve_machine(registry_path: Path, machine: str | None = None) -> tuple[str, dict[str, Any]]:
    machines = (load_yaml(registry_path).get("machines") or {})
    requested = machine.split(".")[0].lower() if machine else None
    if requested:
        for name, cfg in machines.items():
            if requested in _machine_candidates(name, cfg):
                return name, cfg
        raise ValueError(f"unknown machine: {machine}")
    hostname = socket.gethostname().split(".")[0].lower()
    for name, cfg in machines.items():
        if hostname in _machine_candidates(name, cfg):
            return name, cfg
    raise ValueError(f"no registry machine matches hostname: {hostname}")


def _normalize_config_path(path: Any) -> str:
    return str(path).replace("\\\\", "\\").rstrip("/\\")


def find_registry_harness_root_divergences(registry_path: Path, harness_path: Path) -> list[dict[str, str]]:
    registry = load_yaml(registry_path).get("machines") or {}
    harness = (load_yaml(harness_path).get("workstations") or {}) if harness_path.exists() else {}
    divergences: list[dict[str, str]] = []
    for name, machine in registry.items():
        reg_root = machine.get("workspace_root")
        h_root = (harness.get(name) or {}).get("ws_hub_path")
        if reg_root and h_root and _normalize_config_path(reg_root) != _normalize_config_path(h_root):
            divergences.append({"machine": name, "registry": str(reg_root), "harness": str(h_root)})
    return divergences


def registry_status(registry_path: Path, harness_path: Path) -> dict[str, Any]:
    registry = load_yaml(registry_path).get("machines") or {}
    missing: list[str] = []
    for name, machine in registry.items():
        if machine.get("repo_layout") == "sibling":
            for field in ("workspace_root", "tier1_repo_root", "repo_layout"):
                if not machine.get(field):
                    missing.append(f"{name}.{field}")
    divergences = find_registry_harness_root_divergences(registry_path, harness_path)
    status = "pass" if not missing and not divergences else "fail"
    return _section(status, missing_fields=missing, divergences=divergences, evidence_paths=[str(registry_path), str(harness_path)])


def classify_provider_skill_path(path: Path, expected_target: str, allow_set: set[Path]) -> dict[str, Any]:
    allow_resolved = {p.resolve(strict=False) for p in allow_set}
    if not path.exists() and not path.is_symlink():
        return {"status": "fail", "kind": "missing", "path": str(path)}
    if path.is_symlink():
        target = os.readlink(path)
        real = path.resolve(strict=False)
        if not real.exists():
            return {"status": "fail", "kind": "broken_symlink", "target": target, "realpath": str(real)}
        if real not in allow_resolved:
            return {"status": "fail", "kind": "symlink_outside_allowset", "target": target, "realpath": str(real)}
        if target != expected_target:
            return {"status": "fail", "kind": "wrong_symlink_target", "target": target, "expected": expected_target}
        if not has_skill_md(real):
            return {"status": "fail", "kind": "target_has_no_skills", "target": target, "realpath": str(real)}
        return {"status": "pass", "kind": "symlink", "target": target, "realpath": str(real)}
    if path.is_file():
        head = path.read_bytes()[:7]
        if head == b"IntxLNK":
            return {"status": "fail", "kind": "corrupted_ntfs_symlink", "repair_action": "unlink_then_recreate", "path": str(path)}
        return {"status": "fail", "kind": "unexpected_regular_file", "path": str(path)}
    if path.is_dir():
        if has_skill_md(path) and path.resolve(strict=False) in allow_resolved:
            return {"status": "pass", "kind": "directory", "path": str(path)}
        return {"status": "fail", "kind": "unexpected_directory", "path": str(path)}
    return {"status": "fail", "kind": "unexpected_file_type", "path": str(path)}


def check_agents_contract(repo_path: Path, workspace_root: Path, tier1_repo_root: Path) -> dict[str, Any]:
    agents = repo_path / "AGENTS.md"
    if not agents.exists():
        return {"status": "fail", "kind": "missing_agents", "path": str(agents)}
    text = agents.read_text(errors="replace")
    if repo_path.name != "workspace-hub" and "../AGENTS.md" in text:
        target = tier1_repo_root / "workspace-hub" / "AGENTS.md"
        return {"status": "fail", "kind": "stale_parent_contract", "target": str(target), "path": str(agents)}
    contract_re = re.compile(r"^Contract:\s+\.\./workspace-hub/AGENTS\.md(?:\s|\||$)", re.MULTILINE)
    if contract_re.search(text):
        target = tier1_repo_root / "workspace-hub" / "AGENTS.md"
        return {"status": "pass" if target.exists() else "fail", "kind": "workspace_hub_contract", "target": str(target)}
    if repo_path.name != "workspace-hub":
        target = tier1_repo_root / "workspace-hub" / "AGENTS.md"
        return {"status": "fail", "kind": "missing_workspace_hub_contract", "target": str(target), "path": str(agents)}
    return {"status": "pass", "kind": "local_contract", "path": str(agents)}


def run_memory_check(root: Path, machine: dict[str, Any] | None = None, local_root: Path | None = None) -> dict[str, Any]:
    machine = machine or {}
    local_root = local_root or root
    target_hostname = str(machine.get("hostname") or "").split(".")[0]
    ssh_target = machine.get("ssh") or target_hostname
    local_hostname = socket.gethostname().split(".")[0]
    if target_hostname and target_hostname != local_hostname:
        remote_root = Path(str(machine.get("workspace_root") or ""))
        script = remote_root / "scripts" / "memory" / "check-memory-drift.sh"
        if machine.get("linux_reachable") is False or not ssh_target:
            return _section(
                "not_present",
                evidence_paths=[f"{target_hostname}:{script}"],
                reason="machine_not_linux_reachable",
            )
        cmd = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
            str(ssh_target),
            f"cd {shlex.quote(str(remote_root))} && bash {shlex.quote(str(script))}",
        ]
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        status = "pass" if result.returncode == 0 else "fail"
        reason = None if result.returncode == 0 else "memory_check_failed"
        if result.returncode == 255:
            reason = "ssh_unreachable"
        return _section(
            status,
            evidence_paths=[f"{target_hostname}:{script}"],
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
            reason=reason,
        )
    script = local_root / "scripts" / "memory" / "check-memory-drift.sh"
    if not script.exists():
        return _section("not_present", evidence_paths=[str(script)])
    result = subprocess.run(["bash", str(script)], cwd=local_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, check=False)
    return _section("pass" if result.returncode == 0 else "fail", evidence_paths=[str(script)], stdout=result.stdout.strip(), stderr=result.stderr.strip())


def sibling_skill_allow_set(workspace_root: Path, tier1_repo_root: Path, repos: list[str]) -> set[Path]:
    allow = {workspace_root / ".claude" / "skills"}
    for repo in repos:
        path = tier1_repo_root / repo / ".claude" / "skills"
        if has_skill_md(path):
            allow.add(path)
    return allow


def check_skills(workspace_root: Path, tier1_repo_root: Path, repos: list[str]) -> dict[str, Any]:
    allow = sibling_skill_allow_set(workspace_root, tier1_repo_root, repos)
    entries: dict[str, Any] = {}
    failures = 0
    for repo in repos:
        repo_path = tier1_repo_root / repo
        if not repo_path.exists():
            entries[repo] = {"status": "not_present", "path": str(repo_path)}
            continue
        expected = "../.claude/skills" if repo == "workspace-hub" else "../../workspace-hub/.claude/skills"
        repo_result = {}
        for provider in (".codex", ".gemini"):
            result = classify_provider_skill_path(repo_path / provider / "skills", expected, allow)
            repo_result[provider] = result
            if result["status"] == "fail":
                failures += 1
        entries[repo] = repo_result
    return _section("fail" if failures else "pass", evidence_paths=[str(workspace_root / ".claude" / "skills")], repos=entries)


def check_harness_contracts(workspace_root: Path, tier1_repo_root: Path, repos: list[str]) -> dict[str, Any]:
    entries = {}
    failures = 0
    for repo in repos:
        repo_path = tier1_repo_root / repo
        if not repo_path.exists():
            entries[repo] = {"status": "not_present", "path": str(repo_path)}
            continue
        result = check_agents_contract(repo_path, workspace_root, tier1_repo_root)
        entries[repo] = result
        if result["status"] == "fail":
            failures += 1
    return _section("fail" if failures else "pass", evidence_paths=[str(workspace_root / "AGENTS.md")], repos=entries)


def build_report(machine_name: str | None = None) -> dict[str, Any]:
    root = repo_root()
    registry_path = root / "config" / "workstations" / "registry.yaml"
    harness_path = root / "scripts" / "readiness" / "harness-config.yaml"
    resolved_name, machine = resolve_machine(registry_path, machine_name)
    workspace_root = Path(str(machine["workspace_root"]))
    tier1_repo_root = Path(str(machine.get("tier1_repo_root") or workspace_root.parent))
    repos = list(machine.get("repos") or [])
    return {
        "machine": resolved_name,
        "memory": run_memory_check(workspace_root, machine, workspace_root),
        "skills": check_skills(workspace_root, tier1_repo_root, repos),
        "harness_contracts": check_harness_contracts(workspace_root, tier1_repo_root, repos),
        "registry": registry_status(registry_path, harness_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(args.machine)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for key in ("memory", "skills", "harness_contracts", "registry"):
            print(f"{key}: {report[key]['status']}")
    return 0 if all(report[key]["status"] in {"pass", "not_present"} for key in ("memory", "skills", "harness_contracts", "registry")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
