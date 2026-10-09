from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from workspace_hub.workstations import task_dispatch


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
FLEET_SSH = REPO_ROOT / "config" / "fleet-ssh-hosts.yml"
HARNESS_CONFIG = REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml"


def test_registry_declares_provider_neutral_task_dispatch_for_five_machines() -> None:
    registry = task_dispatch.load_registry(REGISTRY)
    records = task_dispatch.dispatch_records(registry)

    assert [record.machine for record in records] == [
        "dev-primary",
        "dev-secondary",
        "gpu-claw",
        "ace-win-1",
        "ace-win-2",
    ]
    assert [record.hostname for record in records] == [
        "ace-linux-1",
        "ace-linux-2",
        "gpu-claw",
        "ace-win-1",
        "ace-win-2",
    ]
    assert all(record.ssh_alias for record in records)
    assert all({"claude", "codex"} <= set(record.providers) for record in records)
    assert all(record.shell in {"bash", "git-bash"} for record in records)
    assert all(
        record.scheduled_task_path
        for record in records
        if record.os == "windows"
    )


def test_task_dispatch_roster_has_twenty_directed_routes() -> None:
    records = task_dispatch.dispatch_records(task_dispatch.load_registry(REGISTRY))
    routes = task_dispatch.directed_routes(records)

    assert len(routes) == 20
    assert len({(route.source, route.target) for route in routes}) == 20
    assert all(route.source != route.target for route in routes)


def test_fleet_ssh_hosts_keeps_hf_scope_but_validates_aliases_against_dispatch_registry() -> None:
    registry = task_dispatch.load_registry(REGISTRY)
    fleet = yaml.safe_load(FLEET_SSH.read_text(encoding="utf-8"))

    assert fleet["ssh_hosts"] == ["ace-linux-2", "gpu-claw"]
    assert fleet["manual_hosts"] == ["ace-win-1", "ace-win-2"]
    task_dispatch.validate_fleet_ssh_hosts(fleet, registry)


def test_harness_config_task_dispatch_fields_match_registry() -> None:
    registry = task_dispatch.load_registry(REGISTRY)
    harness = yaml.safe_load(HARNESS_CONFIG.read_text(encoding="utf-8"))

    task_dispatch.validate_harness_config(harness, registry)


def test_route_evidence_fails_closed_when_missing_stale_or_blocked() -> None:
    records = task_dispatch.dispatch_records(task_dispatch.load_registry(REGISTRY))
    now = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
    evidence = {
        ("dev-primary", "dev-secondary"): {
            "generated_at": now.isoformat(),
            "status": "pass",
            "checks": {name: True for name in task_dispatch.REQUIRED_ROUTE_CHECKS},
        },
        ("dev-primary", "gpu-claw"): {
            "generated_at": (now - timedelta(hours=49)).isoformat(),
            "status": "pass",
            "checks": {name: True for name in task_dispatch.REQUIRED_ROUTE_CHECKS},
        },
        ("dev-primary", "ace-win-1"): {
            "generated_at": now.isoformat(),
            "status": "blocked",
            "checks": {name: True for name in task_dispatch.REQUIRED_ROUTE_CHECKS},
        },
    }

    verdicts = task_dispatch.route_verdicts(records, evidence, now=now, max_age_hours=24)

    assert verdicts[("dev-primary", "dev-secondary")] == "READY"
    assert verdicts[("dev-primary", "gpu-claw")] == "STALE-EVIDENCE"
    assert verdicts[("dev-primary", "ace-win-1")] == "BLOCKED"
    assert verdicts[("dev-secondary", "dev-primary")] == "MISSING-EVIDENCE"


def test_registry_task_dispatch_rejects_client_names() -> None:
    registry = task_dispatch.load_registry(REGISTRY)

    forbidden = task_dispatch.find_public_repo_forbidden_names(registry)

    assert forbidden == []


@pytest.mark.parametrize("field", sorted(task_dispatch.REQUIRED_ROUTE_CHECKS))
def test_route_evidence_requires_every_dispatch_check(field: str) -> None:
    records = task_dispatch.dispatch_records(task_dispatch.load_registry(REGISTRY))
    now = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
    checks = {name: True for name in task_dispatch.REQUIRED_ROUTE_CHECKS}
    del checks[field]
    evidence = {
        ("dev-primary", "dev-secondary"): {
            "generated_at": now.isoformat(),
            "status": "pass",
            "checks": checks,
        },
    }

    verdicts = task_dispatch.route_verdicts(records, evidence, now=now, max_age_hours=24)

    assert verdicts[("dev-primary", "dev-secondary")] == "MISSING-EVIDENCE"
