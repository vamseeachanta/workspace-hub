"""TDD tests for #2720 Telegram/Hermes host readiness."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "readiness" / "telegram_hermes_readiness.py"
spec = importlib.util.spec_from_file_location("telegram_hermes_readiness", MODULE_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["telegram_hermes_readiness"] = module
spec.loader.exec_module(module)


def _registry(tmp_path: Path) -> Path:
    data = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "os": "linux",
                "role": "primary-dev",
                "workspace_root": str(tmp_path / "workspace-hub"),
                "capabilities": {"tools": ["git", "gh", "hermes"], "agent_clis": ["claude"], "gpu": False},
                "storage": {"local": str(tmp_path), "knowledge": str(tmp_path / "ace"), "remote_mounts": []},
                "repos": ["workspace-hub", "digitalmodel"],
                "telegram_hermes": {
                    "dispatch_enabled": True,
                    "telegram_mode": "coordinator",
                    "hermes_profile": "default",
                    "sync_policy": "pull-before-work-push-after-work",
                    "data_access_profile": {"repos": ["workspace-hub", "digitalmodel"], "storage_roots": [str(tmp_path)], "remote_mounts": []},
                    "readiness_freshness_thresholds": {"report_hours": 25},
                },
            },
            "licensed-win-1": {
                "hostname": "licensed-win-1",
                "os": "windows",
                "role": "simulation-license-host",
                "workspace_root": "D:\\workspace-hub",
                "capabilities": {"tools": ["git", "orcaflex"], "agent_clis": ["claude"], "gpu": False},
                "storage": {"local": "D:\\", "knowledge": None, "remote_mounts": []},
                "repos": ["OGManufacturing"],
                "telegram_hermes": {
                    "dispatch_enabled": False,
                    "telegram_mode": "desktop-status-only",
                    "hermes_profile": "windows-git-bash",
                    "sync_policy": "manual-status-only",
                    "data_access_profile": {"repos": ["OGManufacturing"], "storage_roots": ["D:\\"], "remote_mounts": []},
                    "readiness_freshness_thresholds": {"report_hours": 25},
                },
            },
            "macbook-portable": {
                "hostname": "Vamsees-MacBook-Air",
                "os": "macos",
                "role": "portable-dev",
                "workspace_root": "/Users/krishna/workspace-hub",
                "capabilities": {"tools": ["git", "gh"], "agent_clis": ["claude"], "gpu": False},
                "storage": {"local": "/Users/krishna", "knowledge": None, "remote_mounts": []},
                "repos": ["workspace-hub"],
                "telegram_hermes": {
                    "dispatch_enabled": False,
                    "telegram_mode": "desktop-status-only",
                    "hermes_profile": "manual",
                    "sync_policy": "manual-status-only",
                    "data_access_profile": {"repos": ["workspace-hub"], "storage_roots": ["/Users/krishna"], "remote_mounts": []},
                    "readiness_freshness_thresholds": {"report_hours": 25},
                },
            },
            "gali-linux-compute-1": {
                "hostname": "shoerack",
                "os": "linux",
                "role": "gpu-compute",
                "workspace_root": None,
                "capabilities": {"tools": ["cuda"], "agent_clis": [], "gpu": "rtx-3090x2"},
                "storage": {"local": None, "knowledge": None, "remote_mounts": []},
                "repos": [],
            },
        }
    }
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    (tmp_path / "workspace-hub").mkdir()
    (tmp_path / "workspace-hub" / "AGENTS.md").write_text("# policy", encoding="utf-8")
    (tmp_path / "ace").mkdir()
    return path


def test_allow_all_users_is_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.setenv("GATEWAY_ALLOW_ALL_USERS", "true")

    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert "GATEWAY_ALLOW_ALL_USERS" in "\n".join(report["hosts"]["dev-primary"]["failures"])
    assert "true" not in json.dumps(report)


def test_cross_os_and_not_onboarded_host_readiness(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")

    report = module.collect_readiness(registry)

    assert report["hosts"]["dev-primary"]["status"] in {"pass", "warn"}
    assert report["hosts"]["licensed-win-1"]["status"] == "status-only"
    assert report["hosts"]["licensed-win-1"]["workspace_root"] == "D:\\workspace-hub"
    assert report["hosts"]["macbook-portable"]["dispatchable"] is False
    assert report["hosts"]["gali-linux-compute-1"]["status"] == "not-onboarded"
    assert report["hosts"]["gali-linux-compute-1"]["dispatchable"] is False


def test_dispatch_host_without_allowlist_is_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert "TELEGRAM_HERMES_ALLOWED_USER_IDS" in "\n".join(report["hosts"]["dev-primary"]["failures"])


def test_malformed_registry_is_fail_closed(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text("machines: [not-a-map", encoding="utf-8")

    report = module.collect_readiness(registry)

    assert report["overall_status"] == "fail"
    assert report["hosts"] == {}
    assert report["errors"]


def test_registry_secret_metadata_is_fail_closed(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-primary"]["telegram_hermes"]["bot_token"] = "123456789:***"
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")

    report = module.collect_readiness(registry)

    rendered = json.dumps(report)
    assert report["overall_status"] == "fail"
    assert report["hosts"] == {}
    assert "secret-like" in rendered
    assert "ABCdef" not in rendered


def test_hostname_alias_selects_logical_host_id(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")

    report = module.collect_readiness(registry, host_id="ace-linux-1")

    assert report["errors"] == []
    assert list(report["hosts"].keys()) == ["dev-primary"]
    assert report["hosts"]["dev-primary"]["hostname"] == "ace-linux-1"


def test_unknown_host_id_is_fail_closed(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    report = module.collect_readiness(registry, host_id="missing-host")

    assert report["overall_status"] == "fail"
    assert report["hosts"] == {}
    assert "missing-host" in report["errors"][0]


def test_live_registry_has_dispatch_metadata_without_secret_fields(monkeypatch) -> None:
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    live_registry = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    data = yaml.safe_load(live_registry.read_text(encoding="utf-8"))

    for host_id, machine in data["machines"].items():
        assert "telegram_hermes" in machine, f"{host_id} missing telegram_hermes metadata"

    report = module.collect_readiness(live_registry)
    rendered = json.dumps(report)
    assert report["errors"] == []
    assert "secret-like" not in rendered
    assert report["hosts"]["dev-primary"]["dispatchable"] is True
    assert report["hosts"]["dev-secondary"]["dispatchable"] is True
    assert report["hosts"]["licensed-win-1"]["status"] == "status-only"
