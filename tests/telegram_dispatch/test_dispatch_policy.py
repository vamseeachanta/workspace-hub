"""TDD tests for the #2720 Telegram/Hermes dispatch policy contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "telegram_dispatch" / "policy.py"
spec = importlib.util.spec_from_file_location("telegram_dispatch_policy", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["telegram_dispatch_policy"] = module
spec.loader.exec_module(module)


def _write_registry(tmp_path: Path) -> Path:
    registry = {
        "machines": {
            "dev-primary": {
                "hostname": "ace-linux-1",
                "os": "linux",
                "role": "primary-dev",
                "workspace_root": "/mnt/local-analysis/workspace-hub",
                "schedule_variant": "full",
                "ssh": "ace-linux-1",
                "capabilities": {"tools": ["git", "gh", "hermes"], "agent_clis": ["claude"], "gpu": False},
                "storage": {"local": "/mnt/local-analysis", "knowledge": "/mnt/ace", "remote_mounts": []},
                "repos": ["workspace-hub", "digitalmodel"],
                "telegram_hermes": {
                    "dispatch_enabled": True,
                    "telegram_mode": "coordinator",
                    "hermes_profile": "default",
                    "sync_policy": "pull-before-work-push-after-work",
                    "data_access_profile": {
                        "repos": ["workspace-hub", "digitalmodel"],
                        "storage_roots": ["/mnt/local-analysis", "/mnt/ace"],
                        "remote_mounts": [],
                    },
                    "readiness_freshness_thresholds": {"report_hours": 25},
                },
            },
            "macbook-portable": {
                "hostname": "Vamsees-MacBook-Air",
                "os": "macos",
                "role": "portable-dev",
                "workspace_root": "/Users/krishna/workspace-hub",
                "schedule_variant": "none",
                "ssh": None,
                "capabilities": {"tools": ["git"], "agent_clis": ["claude"], "gpu": False},
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
        }
    }
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(registry), encoding="utf-8")
    return path


def test_registry_extends_existing_workstation_schema(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)

    hosts = module.load_registry(registry_path)

    assert set(hosts) == {"dev-primary", "macbook-portable"}
    assert hosts["dev-primary"].dispatch_enabled is True
    assert hosts["dev-primary"].telegram_mode == "coordinator"
    assert hosts["dev-primary"].workspace_root == "/mnt/local-analysis/workspace-hub"
    assert hosts["macbook-portable"].dispatch_enabled is False


def test_load_registry_rejects_secret_values(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    data["machines"]["dev-primary"]["telegram_hermes"]["bot_token"] = "123456789:" + ("A" * 32)
    registry_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(module.DispatchPolicyError, match="secret-like value") as exc:
        module.load_registry(registry_path)

    assert "ABCdef" not in str(exc.value)
    assert "bot_token" in str(exc.value)


def test_load_registry_rejects_dispatch_enabled_status_only_modes(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    tg = data["machines"]["macbook-portable"]["telegram_hermes"]
    tg["dispatch_enabled"] = True

    for bad_mode in ("desktop-status-only", "disabled"):
        tg["telegram_mode"] = bad_mode
        registry_path.write_text(yaml.safe_dump(data), encoding="utf-8")

        with pytest.raises(module.DispatchPolicyError, match="dispatch_enabled requires telegram_mode"):
            module.load_registry(registry_path)


def _verified_empty_lease_snapshot():
    return module.LeaseSnapshot(fetched_ok=True, source="git-remote", leases=[])


def test_dispatch_blocks_unapproved_implementation_issue(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    request = module.DispatchRequest(command="/dispatch 2720 --host dev-primary", issue_number=2720, mode="implementation", host_selector="dev-primary")
    issue = module.IssueState(number=2720, labels=["status:plan-review"], url="https://github.com/example/issues/2720")
    readiness = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}

    result = module.evaluate_dispatch_request(request, issue, registry_path, tmp_path / ".planning" / "plan-approved", readiness, lease_snapshot=_verified_empty_lease_snapshot())

    assert result.accepted is False
    assert result.reason_code == "approval_required"
    assert "status:plan-approved" in result.message
    assert result.lease_ref is None


def test_dispatch_blocks_plan_approved_without_local_marker(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    request = module.DispatchRequest(command="/dispatch 2720 --host dev-primary", issue_number=2720, mode="implementation", host_selector="dev-primary")
    issue = module.IssueState(number=2720, labels=["status:plan-approved"], url="https://github.com/example/issues/2720")
    readiness = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}

    result = module.evaluate_dispatch_request(request, issue, registry_path, tmp_path / ".planning" / "plan-approved", readiness, lease_snapshot=_verified_empty_lease_snapshot())

    assert result.accepted is False
    assert result.reason_code == "approval_marker_missing"
    assert ".planning/plan-approved/2720.md" in result.message
    assert result.lease_ref is None


def test_dispatch_blocks_issue_identity_mismatch_even_with_approved_resolved_issue(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    marker_dir = tmp_path / ".planning" / "plan-approved"
    marker_dir.mkdir(parents=True)
    (marker_dir / "9999.md").write_text("approved", encoding="utf-8")
    request = module.DispatchRequest(command="/dispatch 2720 --host dev-primary", issue_number=2720, mode="implementation", host_selector="dev-primary")
    issue = module.IssueState(number=9999, labels=["status:plan-approved"], url="https://github.com/example/issues/9999")
    readiness = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}

    result = module.evaluate_dispatch_request(request, issue, registry_path, marker_dir, readiness, lease_snapshot=_verified_empty_lease_snapshot())

    assert result.accepted is False
    assert result.reason_code == "issue_mismatch"
    assert result.lease_ref is None


def test_dispatch_blocks_when_remote_lease_state_is_unknown(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    marker_dir = tmp_path / ".planning" / "plan-approved"
    marker_dir.mkdir(parents=True)
    (marker_dir / "2720.md").write_text("approved", encoding="utf-8")
    request = module.DispatchRequest(command="/dispatch 2720 --host dev-primary", issue_number=2720, mode="implementation", host_selector="dev-primary")
    issue = module.IssueState(number=2720, labels=["status:plan-approved"], url="https://github.com/example/issues/2720")
    readiness = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}

    result = module.evaluate_dispatch_request(
        request,
        issue,
        registry_path,
        marker_dir,
        readiness,
        lease_snapshot=module.LeaseSnapshot(fetched_ok=False, source="git ls-remote failed", leases=[]),
    )

    assert result.accepted is False
    assert result.reason_code == "lease_state_unknown"
    assert result.lease_ref is None


def test_dispatch_allows_plan_only_for_needs_plan(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    request = module.DispatchRequest(command="/dispatch 2720 --mode plan --host dev-primary", issue_number=2720, mode="plan", host_selector="dev-primary")
    issue = module.IssueState(number=2720, labels=["status:needs-plan"], url="https://github.com/example/issues/2720")
    readiness = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}

    result = module.evaluate_dispatch_request(request, issue, registry_path, tmp_path / ".planning" / "plan-approved", readiness, lease_snapshot=_verified_empty_lease_snapshot())

    assert result.accepted is True
    assert result.reason_code == "accepted"
    assert result.host_id == "dev-primary"
    assert result.lease_ref == "refs/heads/dispatch/leases/2720-plan"


def test_dispatch_blocks_dirty_repo_and_duplicate_lease(tmp_path: Path) -> None:
    registry_path = _write_registry(tmp_path)
    marker_dir = tmp_path / ".planning" / "plan-approved"
    marker_dir.mkdir(parents=True)
    (marker_dir / "2720.md").write_text("approved", encoding="utf-8")
    request = module.DispatchRequest(command="/dispatch 2720 --host dev-primary", issue_number=2720, mode="implementation", host_selector="dev-primary")
    issue = module.IssueState(number=2720, labels=["status:plan-approved"], url="https://github.com/example/issues/2720")

    dirty = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=True, ahead=0, behind=0, missing_data=[])}
    dirty_result = module.evaluate_dispatch_request(request, issue, registry_path, marker_dir, dirty, lease_snapshot=_verified_empty_lease_snapshot())
    assert dirty_result.accepted is False
    assert dirty_result.reason_code == "repo_not_clean"

    clean = {"dev-primary": module.HostReadiness(host_id="dev-primary", status="pass", dirty=False, ahead=0, behind=0, missing_data=[])}
    active_lease = module.DispatchLease(issue_number=2720, mode="implementation", host_id="dev-primary", job_id="job-existing", lease_ref="refs/heads/dispatch/leases/2720-implementation", active=True)
    duplicate_snapshot = module.LeaseSnapshot(fetched_ok=True, source="git-remote", leases=[active_lease])
    duplicate_result = module.evaluate_dispatch_request(request, issue, registry_path, marker_dir, clean, lease_snapshot=duplicate_snapshot)
    assert duplicate_result.accepted is False
    assert duplicate_result.reason_code == "duplicate_lease"
    assert "job-existing" in duplicate_result.message


def test_command_contract_supports_status_jobs_sync_and_dispatch() -> None:
    status = module.parse_telegram_command("/status --host dev-primary")
    jobs = module.parse_telegram_command("/jobs")
    sync = module.parse_telegram_command("/sync --host dev-secondary")
    dispatch = module.parse_telegram_command("/dispatch 2720 --mode plan --host dev-primary")

    assert status.command_type == "status"
    assert status.host_selector == "dev-primary"
    assert jobs.command_type == "jobs"
    assert sync.command_type == "sync"
    assert sync.host_selector == "dev-secondary"
    assert dispatch.command_type == "dispatch"
    assert dispatch.issue_number == 2720


def test_unparseable_telegram_command_is_rejected() -> None:
    with pytest.raises(module.DispatchPolicyError, match="usage"):
        module.parse_dispatch_command("/dispatch --host dev-primary")
    with pytest.raises(module.DispatchPolicyError, match="usage"):
        module.parse_dispatch_command("/dispatch 0 --host dev-primary")
    with pytest.raises(module.DispatchPolicyError, match="usage"):
        module.parse_dispatch_command("/dispatch -1 --host dev-primary")
    with pytest.raises(module.DispatchPolicyError, match="usage"):
        module.parse_telegram_command("/sync --dangerously-force")
