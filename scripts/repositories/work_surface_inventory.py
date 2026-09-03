#!/usr/bin/env python3
"""Build a public-safe inventory of declared repositories and local contract coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

PROFILES = {"code", "knowledge", "control-product"}
SENSITIVITIES = {
    "public", "business-internal", "client-confidential", "personal-sensitive", "unclassified"
}


def load_declared_repositories(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    declared: dict[str, dict[str, Any]] = {}
    for raw in data.get("repos", []):
        name = raw.get("repo")
        if not isinstance(name, str) or not name or name in declared:
            raise ValueError(f"invalid or duplicate repository name: {name!r}")
        if raw.get("profile") not in PROFILES:
            raise ValueError(f"invalid profile for {name}")
        if raw.get("sensitivity") not in SENSITIVITIES:
            raise ValueError(f"invalid sensitivity for {name}")
        if not isinstance(raw.get("mcp_required"), bool):
            raise ValueError(f"mcp_required must be boolean for {name}")
        declared[name] = raw
    return declared


def load_machine_repositories(path: Path, machine: str) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    record = data.get("machines", {}).get(machine, {})
    return {name for name in record.get("repos", []) if isinstance(name, str)}


def _contract(repo: Path, mcp_required: bool, sensitivity: str) -> dict[str, Any]:
    facts = {
        "agents_md": (repo / "AGENTS.md").is_file(),
        "claude_dir": (repo / ".claude").is_dir(),
        "claude_in_dir": (repo / ".claude" / "CLAUDE.md").is_file(),
        "codex_dir": (repo / ".codex").is_dir(),
        "gemini_dir": (repo / ".gemini").is_dir(),
        "root_claude_md": (repo / "CLAUDE.md").is_file(),
        "mcp": "present" if (repo / ".mcp.json").is_file() else (
            "missing-required" if mcp_required else "not-required"),
    }
    required = ("agents_md", "claude_dir", "claude_in_dir", "codex_dir", "gemini_dir")
    facts["complete"] = (
        all(facts[key] for key in required)
        and facts["mcp"] != "missing-required"
        and sensitivity != "unclassified"
    )
    return facts


def _missing_contract(mcp_required: bool) -> dict[str, Any]:
    return {
        "agents_md": False, "claude_dir": False, "claude_in_dir": False,
        "codex_dir": False, "gemini_dir": False, "root_claude_md": False,
        "mcp": "missing-required" if mcp_required else "not-required", "complete": False,
    }


def observe_work_surface(
    workspace_root: Path, declared_names: set[str]
) -> tuple[dict[str, dict[str, Any]], int]:
    observed: dict[str, dict[str, Any]] = {}
    unexpected = 0
    for child in workspace_root.iterdir():
        if child.is_symlink():
            if child.name in declared_names:
                observed[child.name] = {"observed_local": False}
            continue
        is_dir = child.is_dir()
        is_repo = is_dir and (child / ".git").exists()
        if child.name not in declared_names:
            unexpected += int(is_repo)
            continue
        observed[child.name] = {
            "observed_local": is_repo, "non_git": is_dir and not is_repo,
            "path": child if is_repo else None,
        }
    return observed, unexpected


def join_inventory(
    declared: dict[str, dict[str, Any]],
    configured: set[str],
    observed: dict[str, dict[str, Any]],
    unexpected_count: int,
) -> dict[str, Any]:
    records = []
    complete = 0
    observed_count = 0
    missing_count = 0
    non_git_count = 0
    for name in sorted(declared):
        meta = declared[name]
        local = bool(observed.get(name, {}).get("observed_local"))
        configured_here = name in configured
        if local:
            repo_path = observed[name].get("path")
            contract = _contract(repo_path, meta["mcp_required"], meta["sensitivity"])
            state = "configured-present" if configured_here else "observed-unregistered"
            observed_count += 1
        elif observed.get(name, {}).get("non_git"):
            contract = _missing_contract(meta["mcp_required"])
            state = "non-git"
            non_git_count += 1
        else:
            contract = _missing_contract(meta["mcp_required"])
            state = "configured-missing" if configured_here else "declared-missing"
            missing_count += 1
        complete += int(contract["complete"])
        records.append({
            "configured_for_machine": configured_here,
            "contract": contract,
            "mcp_required": meta["mcp_required"],
            "name": name,
            "observed_local": local,
            "profile": meta["profile"],
            "sensitivity": meta["sensitivity"],
            "state": state,
        })
    return {
        "repositories": records,
        "schema_version": 1,
        "summary": {
            "adapter_coverage": {"complete": complete, "incomplete": len(declared) - complete},
            "contract_complete": complete,
            "configured": len(configured),
            "declared": len(declared),
            "missing": missing_count,
            "non_git": non_git_count,
            "observed_declared": observed_count,
            "present": observed_count,
            "unexpected_count": unexpected_count,
            "unknown": unexpected_count,
        },
    }


def build_inventory(mission_map: Path, workstation_registry: Path,
                    workspace_root: Path, machine: str) -> dict[str, Any]:
    declared = load_declared_repositories(mission_map)
    configured = load_machine_repositories(workstation_registry, machine)
    observed, unexpected = observe_work_surface(workspace_root, set(declared))
    return join_inventory(declared, configured, observed, unexpected)


def render_markdown(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    lines = [
        "# Workspace Repository Overview", "",
        "> Generated by `scripts/repositories/work_surface_inventory.py`. Do not edit manually.", "",
        "This is discovery evidence only. It is not a routing, placement, or membership authority.", "",
        "## Summary", "",
        f"- Declared repositories: {summary['declared']}",
        f"- Configured for this machine: {summary['configured']}",
        f"- Present Git repositories: {summary['present']}",
        f"- Missing declared repositories: {summary['missing']}",
        f"- Declared non-Git directories: {summary['non_git']}",
        f"- Declared repositories observed locally: {summary['observed_declared']}",
        f"- Complete provider contracts: {summary['contract_complete']}",
        f"- Incomplete provider contracts: {summary['adapter_coverage']['incomplete']}",
        f"- Undeclared local repositories: {summary['unexpected_count']} (names suppressed)", "",
        "## Declared repositories", "",
        "| Repository | Profile | Sensitivity | State | Machine configured | Local | Contract |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for item in inventory["repositories"]:
        lines.append(
            f"| {item['name']} | {item['profile']} | {item['sensitivity']} | {item['state']} | "
            f"{'yes' if item['configured_for_machine'] else 'no'} | "
            f"{'yes' if item['observed_local'] else 'no'} | "
            f"{'complete' if item['contract']['complete'] else 'incomplete'} |"
        )
    return "\n".join(lines) + "\n"


def write_or_check(path: Path, content: str, check: bool) -> bool:
    if check:
        return path.is_file() and path.read_text(encoding="utf-8") == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, default=root.parent)
    parser.add_argument("--machine", default="macbook-portable")
    parser.add_argument("--mission-map", type=Path, default=root / "config/mission/mission-map.yaml")
    parser.add_argument("--workstations", type=Path, default=root / "config/workstations/registry.yaml")
    parser.add_argument("--json-output", type=Path, default=root / "docs/reports/work-surface-inventory.json")
    parser.add_argument("--markdown-output", type=Path, default=root / "docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inventory = build_inventory(args.mission_map, args.workstations, args.workspace_root, args.machine)
    json_text = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    ok_json = write_or_check(args.json_output, json_text, args.check)
    ok_md = write_or_check(args.markdown_output, render_markdown(inventory), args.check)
    if args.check and not (ok_json and ok_md):
        return 1
    if not args.check:
        print(json.dumps(inventory["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
