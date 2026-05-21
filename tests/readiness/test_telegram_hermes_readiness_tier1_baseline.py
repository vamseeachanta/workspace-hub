from __future__ import annotations

import importlib.util
import json
import shutil
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "readiness" / "telegram_hermes_readiness.py"
REGISTRY_PATH = ROOT / "config" / "workstations" / "registry.yaml"
REQUIRED = ["workspace-hub", "digitalmodel", "assetutilities", "worldenergydata", "llm-wiki", "assethold"]
OPTIONAL = ["aceengineer-website", "aceengineer-strategy"]
NON_TIER1 = [
    "aceengineer-admin",
    "achantas-data",
    "achantas-media",
    "CAD-DEVELOPMENTS",
    "hobbies",
    "kaggle-rogii-2026",
    "llm-wiki-acma",
    "sabithaandkrishnaestates",
    "teamresumes",
]


def load_module():
    spec = importlib.util.spec_from_file_location("telegram_hermes_readiness", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def git_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True, text=True)


def registry_for(tmp_path: Path, *, optional: bool = True, non_tier1: bool = True) -> Path:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = socket.gethostname()
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    git_dir(tmp_path / "workspace-hub")
    (tmp_path / "workspace-hub" / "AGENTS.md").write_text("# test\n", encoding="utf-8")
    for repo in REQUIRED:
        git_dir(tmp_path / repo)
    if optional:
        for repo in OPTIONAL:
            git_dir(tmp_path / repo)
    if non_tier1:
        for repo in NON_TIER1:
            git_dir(tmp_path / repo)
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_readiness_payload_adds_host_scoped_repo_placement(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    registry = registry_for(tmp_path)
    shutil.rmtree(tmp_path / "digitalmodel" / ".git")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(module, "_collect_git_sync_state", lambda root: (False, 0, 0, []))
    report = module.collect_readiness(registry, host_id="dev-primary")
    host = report["hosts"]["dev-primary"]
    assert "repo_placement" in host
    assert host["repo_placement"]["source"] == "scripts/workstations/check-tier1-repo-baseline.py"
    assert host["repo_placement"]["dispatchable"] is False
    assert any("required repo missing" in item["message"] for item in host["repo_placement"]["blockers"])
    assert any("repo placement blockers" in failure for failure in host["failures"])
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert report["overall_status"] == "fail"


def test_warning_only_repo_placement_matches_existing_readiness_policy(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    registry = registry_for(tmp_path, optional=False, non_tier1=True)
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(module, "_collect_git_sync_state", lambda root: (False, 0, 0, []))
    report = module.collect_readiness(registry, host_id="dev-primary")
    host = report["hosts"]["dev-primary"]
    assert any(item["code"] == "git_upstream_missing" for item in host["repo_placement"]["blockers"])
    assert any("optional repo missing" in item["message"] for item in host["repo_placement"]["warnings"])
    assert any("repo placement blockers" in failure for failure in host["failures"])
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert report["overall_status"] == "fail"


def test_inventory_timestamp_is_injected_for_deterministic_readiness_payload(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    registry = registry_for(tmp_path)
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(module, "_collect_git_sync_state", lambda root: (False, 0, 0, []))
    report = module.collect_readiness(registry, host_id="dev-primary")
    assert report["hosts"]["dev-primary"]["repo_placement"]["inventory_timestamp_utc"] == "2026-05-21T00:00:00Z"


def test_repo_placement_failure_uses_injected_timestamp_for_deterministic_payload(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    registry = registry_for(tmp_path)
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(module, "_collect_git_sync_state", lambda root: (False, 0, 0, []))

    def fail_loader():
        raise RuntimeError("boom")

    monkeypatch.setattr(module, "_load_repo_placement_checker", fail_loader)
    report = module.collect_readiness(registry, host_id="dev-primary")
    placement = report["hosts"]["dev-primary"]["repo_placement"]
    assert placement["dispatchable"] is False
    assert placement["inventory_timestamp_utc"] == "2026-05-21T00:00:00Z"
    assert placement["blockers"] == [
        {"code": "repo_placement_unavailable", "message": "repo placement checker unavailable: RuntimeError"}
    ]


def test_remote_dev_primary_uses_host_local_evidence_without_local_repo_probe(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "pass",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
        "repo_placement": {
            "source": module.REPO_PLACEMENT_CHECKER_SOURCE,
            "dispatchable": True,
            "blockers": [],
            "warnings": [],
            "inventory_timestamp_utc": "2026-05-21T00:00:00Z",
        },
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    def forbidden_loader():
        raise AssertionError("remote host must not run local repo placement checker")

    monkeypatch.setattr(module, "_load_repo_placement_checker", forbidden_loader)
    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"] == evidence["repo_placement"]
    assert not any("repo placement blockers" in failure for failure in host["failures"])
    assert host["status"] == "pass"
    assert host["dispatchable"] is True


def test_remote_dev_primary_fails_closed_when_repo_placement_evidence_missing(tmp_path: Path) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "pass",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"]["dispatchable"] is False
    assert host["repo_placement"]["blockers"] == [
        {"code": "repo_placement_missing", "message": "host-local repo placement evidence missing or malformed"}
    ]
    assert "repo placement blockers: 1" in host["failures"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False


def test_remote_dev_primary_fails_closed_when_repo_placement_evidence_malformed(tmp_path: Path) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "pass",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
        "repo_placement": {"dispatchable": False, "blockers": [], "warnings": []},
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"]["dispatchable"] is False
    assert host["repo_placement"]["blockers"] == [
        {"code": "repo_placement_malformed", "message": "host-local repo placement evidence malformed"}
    ]
    assert "repo placement blockers: 1" in host["failures"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False


def test_remote_dev_primary_fails_closed_when_repo_placement_blocker_items_are_malformed(tmp_path: Path) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "fail",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
        "repo_placement": {
            "source": module.REPO_PLACEMENT_CHECKER_SOURCE,
            "dispatchable": False,
            "blockers": ["bad-blocker-shape"],
            "warnings": [],
            "inventory_timestamp_utc": "2026-05-21T00:00:00Z",
        },
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"]["blockers"] == [
        {"code": "repo_placement_malformed", "message": "host-local repo placement evidence malformed"}
    ]
    assert "repo placement blockers: 1" in host["failures"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False


def test_remote_dev_primary_fails_closed_when_repo_placement_items_lack_required_fields(tmp_path: Path) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    machine["repo_layout"] = "sibling"
    machine["tier1_baseline"]["repo_root"] = str(tmp_path)
    machine["tier1_baseline"]["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_baseline"]["layout"] = "sibling"
    machine["telegram_hermes"]["readiness_now"] = "2026-05-21T00:00:00Z"
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "fail",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
        "repo_placement": {
            "source": module.REPO_PLACEMENT_CHECKER_SOURCE,
            "dispatchable": False,
            "blockers": [{"code": "required_missing"}],
            "warnings": [],
            "inventory_timestamp_utc": "2026-05-21T00:00:00Z",
        },
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"]["blockers"] == [
        {"code": "repo_placement_malformed", "message": "host-local repo placement evidence malformed"}
    ]
    assert "repo placement blockers: 1" in host["failures"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False


def test_remote_dev_primary_honors_repo_placement_blockers_from_host_local_evidence(tmp_path: Path) -> None:
    module = load_module()
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    machine = data["machines"]["dev-primary"]
    machine["hostname"] = "ace-linux-1-remote-test"
    machine["hostname_aliases"] = []
    machine["workspace_root"] = str(tmp_path / "workspace-hub")
    machine["tier1_repo_root"] = str(tmp_path)
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    repo_placement = {
        "source": module.REPO_PLACEMENT_CHECKER_SOURCE,
        "dispatchable": False,
        "blockers": [{"code": "required_missing", "message": "required repo missing: digitalmodel", "repo": "digitalmodel"}],
        "warnings": [],
        "inventory_timestamp_utc": "2026-05-21T00:00:00Z",
    }
    evidence = {
        "evidence_type": module.EXPECTED_EVIDENCE_TYPE,
        "schema_version": 1,
        "producer": module.EXPECTED_EVIDENCE_PRODUCER,
        "host_id": "dev-primary",
        "hostname": "ace-linux-1-remote-test",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "fail",
        "dirty": False,
        "ahead": 0,
        "behind": 0,
        "missing_data": [],
        "failures": [],
        "warnings": [],
        "host_local_checks": {
            "env_gates": True,
            "tool_contract": True,
            "workspace_contract": True,
            "git_sync": True,
            "data_access": True,
        },
        "repo_placement": repo_placement,
    }
    (evidence_dir / "dev-primary.json").write_text(json.dumps(evidence), encoding="utf-8")

    report = module.collect_readiness(registry, host_id="dev-primary", evidence_dir=evidence_dir)
    host = report["hosts"]["dev-primary"]
    assert host["repo_placement"] == repo_placement
    assert "repo placement blockers: 1" in host["failures"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
