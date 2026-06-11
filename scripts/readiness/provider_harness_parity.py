#!/usr/bin/env python3
"""Provider harness capability collector for the equality matrix (#2889).

The output is deliberately small and secrets-safe: booleans, closed enums, and reason
codes only. This helper uses only the Python standard library because the Windows
collector may invoke it through a bare `python` executable.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

PROVIDERS = ("claude", "codex", "hermes")
CAPABILITIES = ("memory:read", "skills:invoke", "workflow:gates")

EXPECTED_DIVERGENCE_REASONS = {
    "external_skill_dirs_configured",
}

GATE_PHRASES = ("Plan ALL issues", "USER APPROVES", "TDD mandatory")


def provider_rows() -> list[str]:
    return [f"harness:{provider}:{capability}"
            for provider in PROVIDERS for capability in CAPABILITIES]


def is_expected_divergence(reason: str) -> bool:
    return reason in EXPECTED_DIVERGENCE_REASONS


def _cap(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def _contains_all(text: str, phrases: tuple[str, ...]) -> bool:
    return all(phrase in text for phrase in phrases)


def _has_skill_tree(path: Path) -> bool:
    try:
        return path.exists() and any(path.glob("*/*/SKILL.md"))
    except OSError:
        return False


def _has_any_file(path: Path) -> bool:
    try:
        return path.is_dir() and any(p.is_file() for p in path.rglob("*"))
    except OSError:
        return False


def _has_any_entry(path: Path) -> bool:
    try:
        return path.is_dir() and any(path.iterdir())
    except OSError:
        return False


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _local_runtime_path(provider: str, home: Path) -> Path | None:
    if provider == "codex":
        return home / ".codex" / "AGENTS.md"
    if provider == "hermes":
        return home / ".hermes" / "SOUL.md"
    return None


def _local_runtime_exists(provider: str, home: Path) -> bool:
    path = _local_runtime_path(provider, home)
    return bool(path and path.exists() and path.is_file())


def _installed(provider: str, home: Path) -> bool:
    return _command_exists(provider) or _local_runtime_exists(provider, home)


def _not_installed() -> dict[str, str]:
    return _cap("absent", "provider_not_installed")


def _memory_read(provider: str, workspace: Path, home: Path, installed: bool) -> dict[str, str]:
    if not installed:
        return _not_installed()
    if provider == "claude":
        for rel in (".claude/memory/context.md", ".claude/memory/agents.md"):
            if (workspace / rel).is_file():
                return _cap("present", "claude_memory_context_found")
        return _cap("absent", "claude_memory_missing")
    if provider == "codex":
        agents = workspace / "config" / "agents" / "codex" / "AGENTS.runtime.md"
        memory = workspace / "config" / "agents" / "codex" / "MEMORY.runtime.md"
        if agents.is_file() and memory.is_file() and "memory" in _read_text(memory).lower():
            return _cap("present", "codex_memory_runtime_found")
        return _cap("absent", "codex_memory_runtime_missing")
    if provider == "hermes":
        runtime = workspace / "config" / "agents" / "hermes" / "SOUL.runtime.md"
        memories = home / ".hermes" / "memories"
        has_memory_file = _has_any_file(memories)
        if runtime.is_file() and has_memory_file:
            return _cap("present", "hermes_memory_store_found")
        return _cap("absent", "hermes_memory_store_missing")
    return _cap("unknown", "unknown_provider")


def _skills_invoke(provider: str, workspace: Path, home: Path, installed: bool) -> dict[str, str]:
    if not installed:
        return _not_installed()
    claude_skills = workspace / ".claude" / "skills"
    if provider == "claude":
        if _has_skill_tree(claude_skills):
            return _cap("present", "repo_skill_tree_found")
        return _cap("absent", "repo_skill_tree_missing")
    if provider == "codex":
        adapter = workspace / ".codex" / "skills"
        if adapter.exists() and not (adapter.is_dir() or adapter.is_symlink()):
            return _cap("absent", "adapter_not_directory_or_symlink")
        if not adapter.exists():
            return _cap("absent", "adapter_missing")
        try:
            adapter_real = adapter.resolve()
            claude_real = claude_skills.resolve()
        except OSError:
            return _cap("absent", "adapter_unresolvable")
        if adapter_real == claude_real or _has_skill_tree(adapter):
            return _cap("present", "codex_skill_adapter_found")
        return _cap("absent", "adapter_target_mismatch")
    if provider == "hermes":
        hermes_skills = home / ".hermes" / "skills"
        hermes_config = home / ".hermes" / "config.yaml"
        config_text = _read_text(hermes_config)
        if str(claude_skills) in config_text or _has_skill_tree(hermes_skills):
            return _cap("present", "hermes_skill_registry_found")
        if _has_any_entry(hermes_skills):
            return _cap("expected_divergence", "external_skill_dirs_configured")
        return _cap("absent", "hermes_skill_registry_missing")
    return _cap("unknown", "unknown_provider")


def _workflow_gates(provider: str, workspace: Path, home: Path, installed: bool) -> dict[str, str]:
    if not installed:
        return _not_installed()
    planning_skill = workspace / ".claude" / "skills" / "coordination" / "issue-planning-mode" / "SKILL.md"
    if provider == "claude":
        text = _read_text(workspace / "AGENTS.md")
        text += "\n" + _read_text(workspace / "config" / "agents" / "claude" / "SOUL.runtime.md")
        if planning_skill.is_file() and _contains_all(text, GATE_PHRASES):
            return _cap("present", "hard_gates_runtime_found")
        return _cap("absent", "hard_gates_runtime_missing")
    runtime = _local_runtime_path(provider, home)
    if not runtime or not runtime.is_file():
        return _cap("absent", "active_runtime_missing")
    text = _read_text(runtime)
    if provider == "codex":
        has_lifecycle = "issue-planning-mode" in text or "mandatory lifecycle skills" in text
        if _contains_all(text, GATE_PHRASES) and has_lifecycle:
            return _cap("present", "codex_agents_runtime_active")
        return _cap("absent", "hard_gates_runtime_missing")
    if provider == "hermes" and _contains_all(text, GATE_PHRASES):
        return _cap("present", "hermes_soul_runtime_active")
    return _cap("absent", "hard_gates_runtime_missing")


def collect_provider_harness(workspace: Path, home: Path) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    for provider in PROVIDERS:
        installed = _installed(provider, home)
        providers[provider] = {
            "present": installed,
            "installed": installed,
            "memory:read": _memory_read(provider, workspace, home, installed),
            "skills:invoke": _skills_invoke(provider, workspace, home, installed),
            "workflow:gates": _workflow_gates(provider, workspace, home, installed),
        }
    return {"schema_version": 1, "providers": providers}


def unknown_provider_harness(reason: str = "collector_unavailable") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "providers": {
            provider: {
                "present": False,
                "installed": False,
                "memory:read": _cap("unknown", reason),
                "skills:invoke": _cap("unknown", reason),
                "workflow:gates": _cap("unknown", reason),
            }
            for provider in PROVIDERS
        },
    }


def _yaml_bool(value: bool) -> str:
    return "true" if value else "false"


def emit_yaml(data: dict[str, Any]) -> str:
    lines = [f"schema_version: {data['schema_version']}", "providers:"]
    for provider in PROVIDERS:
        record = data["providers"][provider]
        lines.append(f"  {provider}:")
        lines.append(f"    present: {_yaml_bool(bool(record['present']))}")
        lines.append(f"    installed: {_yaml_bool(bool(record['installed']))}")
        for capability in CAPABILITIES:
            cap = record[capability]
            lines.append(
                f"    \"{capability}\": "
                f"{{status: {cap['status']}, reason: {cap['reason']}}}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--home", default=os.environ.get("HOME", ""))
    parser.add_argument("--format", choices=("yaml", "json"), default="yaml")
    args = parser.parse_args()

    data = collect_provider_harness(Path(args.workspace), Path(args.home))
    if args.format == "json":
        print(json.dumps(data, sort_keys=True))
    else:
        print(emit_yaml(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
