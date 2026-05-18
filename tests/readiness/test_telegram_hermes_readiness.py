"""TDD tests for #2720 Telegram/Hermes host readiness."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
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
    _init_synced_git_repo(tmp_path / "workspace-hub", tmp_path / "origin.git")
    (tmp_path / "ace").mkdir()
    return path


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _init_synced_git_repo(repo: Path, origin: Path) -> None:
    _run_git(repo, "init")
    _run_git(repo, "config", "user.email", "test@example.invalid")
    _run_git(repo, "config", "user.name", "Test User")
    _run_git(repo, "add", "AGENTS.md")
    _run_git(repo, "commit", "-m", "initial")
    subprocess.run(["git", "init", "--bare", str(origin)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _run_git(repo, "remote", "add", "origin", str(origin))
    _run_git(repo, "push", "-u", "origin", "HEAD")


def _valid_remote_evidence(**overrides: object) -> dict[str, object]:
    evidence: dict[str, object] = {
        "evidence_type": "telegram-hermes-host-local-readiness",
        "schema_version": 1,
        "producer": "scripts/readiness/telegram_hermes_readiness.py",
        "host_id": "dev-secondary",
        "hostname": "ace-linux-2",
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
    evidence.update(overrides)
    return evidence


def test_allow_all_users_is_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.setenv("GATEWAY_ALLOW_ALL_USERS", "true")

    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")
    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert "GATEWAY_ALLOW_ALL_USERS" in "\n".join(report["hosts"]["dev-primary"]["failures"])
    assert "true" not in json.dumps(report)


def test_cross_os_and_not_onboarded_host_readiness(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry)

    assert report["hosts"]["dev-primary"]["status"] == "pass"
    assert report["hosts"]["licensed-win-1"]["status"] == "status-only"
    assert report["hosts"]["licensed-win-1"]["workspace_root"] == "D:\\workspace-hub"
    assert report["hosts"]["macbook-portable"]["dispatchable"] is False
    assert report["hosts"]["gali-linux-compute-1"]["status"] == "not-onboarded"
    assert report["hosts"]["gali-linux-compute-1"]["dispatchable"] is False
    for host in report["hosts"].values():
        assert {"dirty", "ahead", "behind", "missing_data"} <= set(host)


def test_remote_dispatch_host_does_not_reuse_local_env_gate(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_BOT_TOKEN", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary")

    host = report["hosts"]["dev-secondary"]
    assert "TELEGRAM_HERMES_ALLOWED_USER_IDS" not in "\n".join(host["failures"])
    assert "TELEGRAM_HERMES_BOT_TOKEN" not in "\n".join(host["failures"])
    assert any("remote" in warning.lower() for warning in host["warnings"])
    assert "host-local-readiness-evidence" in host["missing_data"]
    assert host["dispatchable"] is False


def test_remote_non_linux_dispatch_host_requires_host_local_evidence(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["remote-macos"] = data["machines"]["dev-primary"] | {
        "hostname": "remote-mac",
        "os": "macos",
        "workspace_root": "/Users/remote/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="remote-macos")

    host = report["hosts"]["remote-macos"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "host-local-readiness-evidence" in host["missing_data"]


def test_local_non_linux_dispatch_host_fails_closed_when_workspace_missing(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    local_name = "local-macos-control"
    data["machines"][local_name] = data["machines"]["dev-primary"] | {
        "hostname": local_name,
        "os": "macos",
        "workspace_root": str(tmp_path / "missing-workspace-hub"),
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.setattr(module.socket, "gethostname", lambda: local_name)
    monkeypatch.setattr(module.socket, "getfqdn", lambda: local_name)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id=local_name)

    host = report["hosts"][local_name]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "workspace_root not present" in "\n".join(host["failures"])


def test_remote_dispatch_host_rejects_malformed_host_local_evidence_values(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence(ahead="oops", missing_data=1)),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "host-local readiness evidence ahead must be an integer" in "\n".join(host["failures"])
    assert "host-local readiness evidence missing_data must be a list" in "\n".join(host["failures"])


def test_cli_accepts_evidence_dir_for_remote_host(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence()),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    assert module.main(["--registry", str(registry), "--host", "dev-secondary", "--evidence-dir", str(evidence_dir)]) == 0

    out = json.loads(capsys.readouterr().out)
    assert out["hosts"]["dev-secondary"]["dispatchable"] is True


def test_remote_dispatch_host_can_load_host_local_readiness_evidence(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence()),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "pass"
    assert host["dispatchable"] is True
    assert "host-local-readiness-evidence" not in host["missing_data"]


def test_remote_dispatch_host_rejects_evidence_without_identity_and_freshness(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps({"status": "pass", "dirty": False, "ahead": 0, "behind": 0, "missing_data": []}),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    failures = "\n".join(host["failures"])
    assert "host-local readiness evidence host_id missing" in failures
    assert "host-local readiness evidence generated_at missing" in failures


def test_remote_dispatch_host_rejects_handcrafted_minimal_pass_evidence(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(
            {
                "host_id": "dev-secondary",
                "hostname": "ace-linux-2",
                "generated_at": datetime.now(UTC).isoformat(),
                "status": "pass",
                "dirty": False,
                "ahead": 0,
                "behind": 0,
                "missing_data": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    failures = "\n".join(host["failures"])
    assert "host-local readiness evidence_type invalid or missing" in failures
    assert "host-local readiness evidence host_local_checks missing" in failures


def test_host_local_cli_writes_evidence_file(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = _registry(tmp_path)
    evidence_dir = tmp_path / "readiness"
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    assert module.main(["--registry", str(registry), "--host", "dev-primary", "--evidence-dir", str(evidence_dir)]) == 0

    out = json.loads(capsys.readouterr().out)
    evidence_path = evidence_dir / "dev-primary.json"
    assert out["hosts"]["dev-primary"]["status"] == "pass"
    assert evidence_path.exists()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["evidence_type"] == "telegram-hermes-host-local-readiness"
    assert evidence["schema_version"] == 1
    assert evidence["host_id"] == "dev-primary"
    assert evidence["host_local_checks"]["env_gates"] is True


def test_remote_evidence_failures_are_redacted_from_cli_output(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    secret = "".join(["123456789", ":", "ABCDEFGHIJKLMNOPQRSTUVWXYZ12"])
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence(status="fail", failures=[f"token leaked {secret}"])),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    assert module.main(["--registry", str(registry), "--host", "dev-secondary", "--evidence-dir", str(evidence_dir)]) == 0

    rendered = capsys.readouterr().out
    assert secret not in rendered
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ12" not in rendered
    assert "[REDACTED]" in rendered


def test_remote_evidence_secret_material_is_redacted_from_collect_readiness(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    secret = "".join(["123456789", ":", "ABCDEFGHIJKLMNOPQRSTUVWXYZ12"])
    private_status = "allowed_user_ids=24680,13579 chat_id=-1009876543210 token leaked " + secret
    fragment_status = "remote evidence leaked fragment ZYXWV"
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(
            _valid_remote_evidence(
                status="fail",
                failures=[private_status, fragment_status],
                warnings=[private_status, fragment_status],
                missing_data=[private_status, fragment_status],
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    rendered = json.dumps(report)
    assert secret not in rendered
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ12" not in rendered
    assert "24680" not in rendered
    assert "13579" not in rendered
    assert "-1009876543210" not in rendered
    assert "ZYXWV" not in rendered
    assert "[REDACTED]" in rendered


def test_remote_evidence_private_telegram_identifiers_are_redacted_from_cli_output(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    private_status = "chat_id=-1009876543210 allowlist=12345,67890 invite=https://t.me/+abcdefghijklmnop phone=+155****4567"
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(
            _valid_remote_evidence(
                status="fail",
                failures=[private_status],
                warnings=[private_status],
                missing_data=[private_status],
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    assert module.main(["--registry", str(registry), "--host", "dev-secondary", "--evidence-dir", str(evidence_dir)]) == 0

    rendered = capsys.readouterr().out
    assert "-1009876543210" not in rendered
    assert "12345" not in rendered
    assert "67890" not in rendered
    assert "t.me/+" not in rendered
    assert "+155****4567" not in rendered
    assert "[REDACTED]" in rendered


def test_host_local_evidence_file_redacts_private_telegram_identifiers(tmp_path: Path, monkeypatch, capsys) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-primary"]["telegram_hermes"]["data_access_profile"]["storage_roots"].append(
        "chat_id=-1009876543210 allowlist=12345,67890 invite=https://t.me/+abcdefghijklmnop phone=+155****4567"
    )
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    assert module.main(["--registry", str(registry), "--host", "dev-primary", "--evidence-dir", str(evidence_dir)]) == 0
    capsys.readouterr()

    rendered = (evidence_dir / "dev-primary.json").read_text(encoding="utf-8")
    assert "-1009876543210" not in rendered
    assert "12345" not in rendered
    assert "67890" not in rendered
    assert "t.me/+" not in rendered
    assert "+155****4567" not in rendered
    assert "[REDACTED]" in rendered


def test_remote_dispatch_host_rejects_stale_host_local_evidence(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence(generated_at=(datetime.now(UTC) - timedelta(hours=26)).isoformat())),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "host-local readiness evidence stale" in "\n".join(host["failures"])


def test_remote_dispatch_host_rejects_unsafe_host_local_evidence(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-secondary"] = data["machines"]["dev-primary"] | {
        "hostname": "ace-linux-2",
        "workspace_root": "/mnt/local-analysis/workspace-hub",
    }
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    evidence_dir = tmp_path / "readiness"
    evidence_dir.mkdir()
    (evidence_dir / "dev-secondary.json").write_text(
        json.dumps(_valid_remote_evidence(dirty=True)),
        encoding="utf-8",
    )
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)

    report = module.collect_readiness(registry, host_id="dev-secondary", evidence_dir=evidence_dir)

    host = report["hosts"]["dev-secondary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "host-local evidence is not clean/pass" in "\n".join(host["failures"])


def test_local_readiness_emits_dispatch_policy_sync_fields(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert isinstance(host["dirty"], bool)
    assert isinstance(host["ahead"], int)
    assert isinstance(host["behind"], int)
    assert isinstance(host["missing_data"], list)


def test_dispatch_host_without_allowlist_is_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert "TELEGRAM_HERMES_ALLOWED_USER_IDS" in "\n".join(report["hosts"]["dev-primary"]["failures"])


def test_dispatch_host_without_bot_token_is_readiness_failure(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.delenv("TELEGRAM_HERMES_BOT_TOKEN", raising=False)

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert report["hosts"]["dev-primary"]["dispatchable"] is False
    assert "TELEGRAM_HERMES_BOT_TOKEN" in "\n".join(report["hosts"]["dev-primary"]["failures"])


def test_dispatch_host_missing_workspace_root_is_fail_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-primary"]["workspace_root"] = str(tmp_path / "missing-workspace-hub")
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert report["hosts"]["dev-primary"]["dispatchable"] is False
    assert "workspace_root not present" in "\n".join(report["hosts"]["dev-primary"]["failures"])


def test_dispatch_host_missing_data_access_root_is_fail_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["dev-primary"]["telegram_hermes"]["data_access_profile"]["storage_roots"].append(str(tmp_path / "missing-data-root"))
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "fail"
    assert report["hosts"]["dev-primary"]["dispatchable"] is False
    assert "data_access_profile.storage_roots missing" in "\n".join(report["hosts"]["dev-primary"]["failures"])


def test_dispatch_host_honors_configured_env_pointer_names(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    tg = data["machines"]["dev-primary"]["telegram_hermes"]
    tg["allowed_user_ids_env"] = "CUSTOM_TELEGRAM_ALLOWED_USERS"
    tg["bot_token_env"] = "CUSTOM_TELEGRAM_BOT_TOKEN"
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", raising=False)
    monkeypatch.delenv("TELEGRAM_HERMES_BOT_TOKEN", raising=False)
    monkeypatch.setenv("CUSTOM_TELEGRAM_ALLOWED_USERS", "12345")
    monkeypatch.setenv("CUSTOM_TELEGRAM_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    assert report["hosts"]["dev-primary"]["status"] == "pass"
    rendered = json.dumps(report)
    assert "secret-like" not in rendered
    assert "fake-token-present" not in rendered


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
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

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
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")
    live_registry = REPO_ROOT / "config" / "workstations" / "registry.yaml"
    data = yaml.safe_load(live_registry.read_text(encoding="utf-8"))

    for host_id, machine in data["machines"].items():
        assert "telegram_hermes" in machine, f"{host_id} missing telegram_hermes metadata"
        tg = machine["telegram_hermes"]
        if tg.get("dispatch_enabled"):
            assert tg.get("bot_token_env"), f"{host_id} dispatch host missing bot_token_env pointer"
            assert tg.get("allowed_user_ids_env"), f"{host_id} dispatch host missing allowed_user_ids_env pointer"

    report = module.collect_readiness(live_registry)
    rendered = json.dumps(report)
    assert report["errors"] == []
    assert "secret-like" not in rendered
    dev_primary = report["hosts"]["dev-primary"]
    assert isinstance(dev_primary["dispatchable"], bool)
    if dev_primary["dispatchable"]:
        assert dev_primary["status"] == "pass"
    else:
        assert dev_primary["status"] in {"fail", "warn"}
        assert dev_primary["failures"]
    assert report["hosts"]["dev-secondary"]["dispatchable"] is False
    assert "host-local readiness evidence missing" in "\n".join(report["hosts"]["dev-secondary"]["failures"])
    assert "host-local-readiness-evidence" in report["hosts"]["dev-secondary"]["missing_data"]
    assert report["hosts"]["licensed-win-1"]["status"] == "status-only"


def test_local_workspace_without_git_metadata_fails_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    workspace = tmp_path / "workspace-hub"
    subprocess.run(["rm", "-rf", str(workspace / ".git")], check=True)
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "workspace_root has no .git metadata" in "\n".join(host["failures"])


def test_local_workspace_without_upstream_fails_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    workspace = tmp_path / "workspace-hub"
    _run_git(workspace, "branch", "--unset-upstream")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert "git upstream tracking branch unavailable" in "\n".join(host["failures"])


def test_local_workspace_dirty_git_state_fails_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    workspace = tmp_path / "workspace-hub"
    (workspace / "dirty.txt").write_text("untracked", encoding="utf-8")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert host["dirty"] is True
    assert "uncommitted or untracked" in "\n".join(host["failures"])


def test_local_workspace_ahead_of_upstream_fails_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    workspace = tmp_path / "workspace-hub"
    (workspace / "new-file.txt").write_text("ahead", encoding="utf-8")
    _run_git(workspace, "add", "new-file.txt")
    _run_git(workspace, "commit", "-m", "ahead change")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert host["ahead"] == 1
    assert "ahead of upstream" in "\n".join(host["failures"])


def test_local_workspace_behind_upstream_fails_closed(tmp_path: Path, monkeypatch) -> None:
    registry = _registry(tmp_path)
    workspace = tmp_path / "workspace-hub"
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(origin), str(clone)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _run_git(clone, "config", "user.email", "test@example.invalid")
    _run_git(clone, "config", "user.name", "Test User")
    (clone / "remote-change.txt").write_text("behind", encoding="utf-8")
    _run_git(clone, "add", "remote-change.txt")
    _run_git(clone, "commit", "-m", "remote change")
    _run_git(clone, "push")
    _run_git(workspace, "fetch", "origin")
    monkeypatch.delenv("GATEWAY_ALLOW_ALL_USERS", raising=False)
    monkeypatch.setenv("TELEGRAM_HERMES_ALLOWED_USER_IDS", "12345")
    monkeypatch.setenv("TELEGRAM_HERMES_BOT_TOKEN", "fake-token-present")

    report = module.collect_readiness(registry, host_id="dev-primary")

    host = report["hosts"]["dev-primary"]
    assert host["status"] == "fail"
    assert host["dispatchable"] is False
    assert host["behind"] == 1
    assert "behind upstream" in "\n".join(host["failures"])
