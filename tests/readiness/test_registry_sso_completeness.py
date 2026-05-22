from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


def load_checker():
    path = Path(__file__).resolve().parents[2] / "scripts" / "readiness" / "check-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_checker", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_machine_fields_complete_for_sibling_machines():
    data = yaml.safe_load(Path("config/workstations/registry.yaml").read_text())
    machines = data["machines"]
    missing = []
    for name, machine in machines.items():
        if machine.get("repo_layout") == "sibling":
            for field in ("workspace_root", "tier1_repo_root", "repo_layout"):
                if not machine.get(field):
                    missing.append(f"{name}.{field}")
    assert missing == []


def test_registry_authoritative_for_machine_roots():
    checker = load_checker()
    divergences = checker.find_registry_harness_root_divergences(
        Path("config/workstations/registry.yaml"), Path("scripts/readiness/harness-config.yaml")
    )
    assert divergences == []


def test_harness_covers_all_registry_sibling_machines():
    registry = yaml.safe_load(Path("config/workstations/registry.yaml").read_text())["machines"]
    harness = yaml.safe_load(Path("scripts/readiness/harness-config.yaml").read_text())["workstations"]
    missing = [name for name, machine in registry.items() if machine.get("repo_layout") == "sibling" and name not in harness]
    assert missing == []


def test_windows_sibling_machines_have_explicit_tier1_roots():
    data = yaml.safe_load(Path("config/workstations/registry.yaml").read_text())
    for name in ("licensed-win-1", "licensed-win-2"):
        machine = data["machines"][name]
        assert machine["repo_layout"] == "sibling"
        assert machine["tier1_repo_root"] == "D:\\"
        assert machine["workspace_root"] == "D:\\workspace-hub"
        assert "uv" in machine["capabilities"]["tools"]
