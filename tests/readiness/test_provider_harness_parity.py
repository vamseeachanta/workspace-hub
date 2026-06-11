"""Provider-harness parity contract tests for #2889.

These tests pin the provider/capability vocabulary and the capability predicates before
the collector and matrix renderer consume them.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "provider_harness_parity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("provider_harness_parity", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace-hub"
    (ws / ".claude" / "skills" / "coordination" / "issue-planning-mode").mkdir(parents=True)
    (ws / ".claude" / "skills" / "coordination" / "issue-planning-mode" / "SKILL.md").write_text("x")
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    (ws / ".claude" / "memory" / "agents.md").write_text("agents")
    (ws / ".codex").mkdir(parents=True)
    (ws / "config" / "agents" / "codex").mkdir(parents=True)
    (ws / "config" / "agents" / "codex" / "AGENTS.runtime.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\nmandatory lifecycle skills\n")
    (ws / "config" / "agents" / "codex" / "MEMORY.runtime.md").write_text("memory readback\n")
    (ws / "config" / "agents" / "claude").mkdir(parents=True)
    (ws / "config" / "agents" / "claude" / "SOUL.runtime.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    (ws / "config" / "agents" / "hermes").mkdir(parents=True)
    (ws / "config" / "agents" / "hermes" / "SOUL.runtime.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    (ws / "AGENTS.md").write_text("Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    return ws


def _bin_with(tmp_path: Path, *names: str) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    for name in names:
        exe = bin_dir / name
        exe.write_text("#!/usr/bin/env bash\nexit 0\n")
        exe.chmod(0o755)
    return bin_dir


def test_provider_harness_constants_use_exact_issue_capability_names():
    mod = _load_module()
    assert mod.PROVIDERS == ("claude", "codex", "hermes")
    assert mod.CAPABILITIES == ("memory:read", "skills:invoke", "workflow:gates")
    assert mod.provider_rows() == [
        "harness:claude:memory:read",
        "harness:claude:skills:invoke",
        "harness:claude:workflow:gates",
        "harness:codex:memory:read",
        "harness:codex:skills:invoke",
        "harness:codex:workflow:gates",
        "harness:hermes:memory:read",
        "harness:hermes:skills:invoke",
        "harness:hermes:workflow:gates",
    ]


def test_skill_adapter_rejects_regular_file_pseudo_symlink(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    (ws / ".codex" / "skills").write_text("../.claude/skills\n")
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    (home / ".codex" / "AGENTS.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\nmandatory lifecycle skills\n")
    bin_dir = _bin_with(tmp_path, "claude", "codex")
    monkeypatch.setenv("PATH", str(bin_dir))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["codex"]["present"] is True
    skill = report["providers"]["codex"]["skills:invoke"]
    assert skill == {"status": "absent", "reason": "adapter_not_directory_or_symlink"}


def test_claude_reference_skills_parity_when_repo_skills_exist(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["claude"]["skills:invoke"]["status"] == "present"


def test_repo_runtime_files_do_not_make_provider_installed(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["codex"]["present"] is False
    assert report["providers"]["codex"]["installed"] is False


def test_codex_memory_read_uses_runtime_and_readback_files(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    (home / ".codex" / "AGENTS.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\nmandatory lifecycle skills\n")
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude", "codex")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["codex"]["memory:read"] == {
        "status": "present",
        "reason": "codex_memory_runtime_found",
    }

    (ws / "config" / "agents" / "codex" / "MEMORY.runtime.md").unlink()
    report = mod.collect_provider_harness(ws, home)
    assert report["providers"]["codex"]["memory:read"] == {
        "status": "absent",
        "reason": "codex_memory_runtime_missing",
    }


def test_workflow_gates_requires_active_local_runtime_path(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude", "codex")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["codex"]["workflow:gates"] == {
        "status": "absent",
        "reason": "active_runtime_missing",
    }


def test_workflow_gates_requires_plan_user_approval_and_tdd_text(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".hermes").mkdir(parents=True)
    (home / ".codex" / "AGENTS.md").write_text(
        "Plan ALL issues\nTDD mandatory\nmandatory lifecycle skills\n")
    (home / ".hermes" / "SOUL.md").write_text("Plan ALL issues\nTDD mandatory\n")
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["codex"]["workflow:gates"] == {
        "status": "absent",
        "reason": "hard_gates_runtime_missing",
    }
    assert report["providers"]["hermes"]["workflow:gates"] == {
        "status": "absent",
        "reason": "hard_gates_runtime_missing",
    }

    (home / ".codex" / "AGENTS.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\nmandatory lifecycle skills\n")
    (home / ".hermes" / "SOUL.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    report = mod.collect_provider_harness(ws, home)
    assert report["providers"]["codex"]["workflow:gates"] == {
        "status": "present",
        "reason": "codex_agents_runtime_active",
    }
    assert report["providers"]["hermes"]["workflow:gates"] == {
        "status": "present",
        "reason": "hermes_soul_runtime_active",
    }


def test_hermes_memory_read_requires_nonempty_memory_store_or_repo_equivalent(
        tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    (home / ".hermes" / "memories").mkdir(parents=True)
    (home / ".hermes" / "SOUL.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["hermes"]["memory:read"] == {
        "status": "absent",
        "reason": "hermes_memory_store_missing",
    }

    (home / ".hermes" / "memories" / "MEMORY.md").write_text("memory\n")
    report = mod.collect_provider_harness(ws, home)
    assert report["providers"]["hermes"]["memory:read"] == {
        "status": "present",
        "reason": "hermes_memory_store_found",
    }


def test_hermes_memory_permission_error_grades_absent(tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    (home / ".hermes" / "memories").mkdir(parents=True)
    (home / ".hermes" / "SOUL.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    def blocked_rglob(self, pattern):
        if self == home / ".hermes" / "memories":
            raise PermissionError("blocked")
        return original_rglob(self, pattern)

    original_rglob = mod.Path.rglob
    monkeypatch.setattr(mod.Path, "rglob", blocked_rglob)

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["hermes"]["memory:read"] == {
        "status": "absent",
        "reason": "hermes_memory_store_missing",
    }


def test_hermes_skill_expected_divergence_requires_nonempty_external_dir(
        tmp_path, monkeypatch):
    mod = _load_module()
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    (home / ".hermes" / "skills").mkdir(parents=True)
    (home / ".hermes" / "SOUL.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\n")
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    report = mod.collect_provider_harness(ws, home)

    assert report["providers"]["hermes"]["skills:invoke"] == {
        "status": "absent",
        "reason": "hermes_skill_registry_missing",
    }

    (home / ".hermes" / "skills" / "README.md").write_text("external skills\n")
    report = mod.collect_provider_harness(ws, home)
    assert report["providers"]["hermes"]["skills:invoke"] == {
        "status": "expected_divergence",
        "reason": "external_skill_dirs_configured",
    }


def test_expected_divergence_is_explicit_reason_only():
    mod = _load_module()
    assert mod.is_expected_divergence("external_skill_dirs_configured") is True
    assert mod.is_expected_divergence("anything_else") is False


def test_provider_harness_helper_cli_emits_yaml_without_external_deps(tmp_path):
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    (home / ".codex" / "AGENTS.md").write_text(
        "Plan ALL issues\nUSER APPROVES\nTDD mandatory\nmandatory lifecycle skills\n")
    env = {**os.environ, "PATH": str(_bin_with(tmp_path, "claude", "codex"))}

    res = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--workspace", str(ws), "--home", str(home),
         "--format", "yaml"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert res.returncode == 0, res.stderr
    data = yaml.safe_load(res.stdout)
    assert data["schema_version"] == 1
    assert data["providers"]["codex"]["workflow:gates"]["status"] == "present"
    forbidden = [str(home / ".codex" / "auth.json"), "gho_", "ghp_", "* * *"]
    assert not any(token in res.stdout for token in forbidden)


def test_provider_harness_helper_json_round_trip(tmp_path, monkeypatch):
    ws = _workspace(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("PATH", str(_bin_with(tmp_path, "claude")))

    res = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--workspace", str(ws), "--home", str(home),
         "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert res.returncode == 0, res.stderr
    data = json.loads(res.stdout)
    assert set(data["providers"]) == {"claude", "codex", "hermes"}
