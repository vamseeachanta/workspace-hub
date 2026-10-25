from __future__ import annotations

import copy
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from workspace_hub.workstations import task_dispatch


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
NOW = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)


def synthetic_registry(count=7):
    return {
        f"role-{index}": {
            "os": "linux",
            "task_dispatch": {
                "enabled": True,
                "ssh_alias": f"target-{index}",
                "providers": ["claude", "codex"],
                "provider_identities": {
                    provider: {"account": "test-account", "configuration": "test-config"}
                    for provider in ("claude", "codex")
                },
                "shell": "bash",
                "evidence_freshness_hours": 24,
            },
        }
        for index in range(count)
    }


def receipt(**changes):
    return {
        "generated_at": NOW.isoformat(),
        "status": "pass",
        "checks": {name: True for name in task_dispatch.REQUIRED_ROUTE_CHECKS},
        **changes,
    }


def complete_evidence(registry):
    evidence = {}
    for route in task_dispatch.directed_routes(task_dispatch.dispatch_records(registry)):
        target = registry[route.target]["task_dispatch"]
        for provider in target["providers"]:
            identity = target["provider_identities"][provider]
            key = (route.source, route.target, provider, identity["account"], identity["configuration"])
            evidence[key] = receipt(
                source=route.source, target=route.target, provider=provider, **identity
            )
    return evidence


def test_registry_dispatch_fields_validate_against_consumers():
    registry = task_dispatch.load_registry(REGISTRY)
    records = task_dispatch.dispatch_records(registry)
    # The deployed subset remains five roles until missing mappings are verified.
    assert len(records) == 5
    assert len(task_dispatch.directed_routes(records)) == 20
    assert [r.machine for r in records] == [
        key for key, raw in registry.items() if raw.get("task_dispatch", {}).get("enabled")
    ]
    assert all({"claude", "codex"} <= set(r.providers) for r in records)
    assert all(r.ssh_alias for r in records)
    assert all(r.shell in {"bash", "git-bash"} for r in records)
    assert all(r.scheduled_task_path for r in records if r.os == "windows")
    for filename, validator in (
        (REPO_ROOT / "config" / "fleet-ssh-hosts.yml", task_dispatch.validate_fleet_ssh_hosts),
        (REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml", task_dispatch.validate_harness_config),
    ):
        validator(yaml.safe_load(filename.read_text()), registry)


def test_seven_role_algorithm_covers_every_directed_pair_and_provider():
    registry = synthetic_registry()
    records = task_dispatch.dispatch_records(registry)
    routes = task_dispatch.directed_routes(records)
    assert len(routes) == len({(r.source, r.target) for r in routes}) == 42
    assert all(r.source != r.target for r in routes)
    evidence = complete_evidence(registry)
    assert len(evidence) == 84
    summary = task_dispatch.task_dispatch_summary(registry, evidence, now=NOW)
    assert summary["status"] == "ready"
    assert summary["ready_routes"] == summary["total_routes"] == 42


def test_source_local_summary_counts_only_outgoing_pairs():
    registry = synthetic_registry()
    evidence = {k: v for k, v in complete_evidence(registry).items() if k[0] == "role-0"}
    summary = task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)
    assert summary["status"] == "ready"
    assert summary["ready_routes"] == summary["total_routes"] == 6
    assert task_dispatch.task_dispatch_summary(registry, evidence, now=NOW)["status"] == "not-ready"
    assert task_dispatch.task_dispatch_summary(registry, evidence, source="unknown", now=NOW)["status"] == "not-ready"


@pytest.mark.parametrize("field", ["provider", "account", "configuration"])
def test_receipts_invalidate_when_intended_identity_changes(field):
    registry = synthetic_registry(2)
    evidence = complete_evidence(registry)
    target = registry["role-1"]["task_dispatch"]
    if field == "provider":
        target["providers"].append("additional")
    else:
        target["provider_identities"]["codex"][field] = "changed"
    summary = task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)
    assert summary["status"] == "not-ready"
    assert summary["missing_routes"] == ["role-0->role-1"]


def test_unqualified_and_partial_provider_receipts_fail_closed():
    registry = synthetic_registry(2)
    evidence = complete_evidence(registry)
    key = next(k for k in evidence if k[0] == "role-0" and k[2] == "codex")
    del evidence[key]
    evidence[("role-0", "role-1")] = receipt()
    assert task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)["status"] == "not-ready"
    evidence = complete_evidence(registry)
    evidence[key]["status"] = "blocked"
    assert task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)["blocked_routes"] == ["role-0->role-1"]
    del registry["role-1"]["task_dispatch"]["provider_identities"]
    assert task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)["status"] == "not-ready"


def test_receipt_payload_must_match_qualified_key():
    registry = synthetic_registry(2)
    evidence = complete_evidence(registry)
    row = next(row for key, row in evidence.items() if key[0] == "role-0")
    row["configuration"] = "different-config"
    assert task_dispatch.task_dispatch_summary(registry, evidence, source="role-0", now=NOW)["status"] == "not-ready"


@pytest.mark.parametrize("window", [0, -1, float("nan"), float("inf"), True, "1"])
def test_registry_rejects_invalid_freshness_windows(window):
    registry = synthetic_registry(2)
    registry["role-0"]["task_dispatch"]["evidence_freshness_hours"] = window
    with pytest.raises(ValueError, match="freshness"):
        task_dispatch.dispatch_records(registry)


@pytest.mark.parametrize("endpoint", ["role-0", "role-1"])
def test_stricter_endpoint_freshness_window_applies(endpoint):
    registry = synthetic_registry(2)
    registry[endpoint]["task_dispatch"]["evidence_freshness_hours"] = 1
    evidence = complete_evidence(registry)
    for row in evidence.values():
        row["generated_at"] = (NOW - timedelta(hours=2)).isoformat()
    result = task_dispatch.task_dispatch_summary(registry, evidence, now=NOW)
    assert result["ready_routes"] == 0
    assert len(result["stale_routes"]) == 2
    registry[endpoint]["task_dispatch"]["evidence_freshness_hours"] = 3
    assert task_dispatch.task_dispatch_summary(registry, evidence, now=NOW)["status"] == "ready"
    assert task_dispatch.task_dispatch_summary(registry, evidence, now=NOW, max_age_hours=1)["status"] == "not-ready"


@pytest.mark.parametrize("stamp", ["2026-10-08T12:00:00", "invalid", None])
def test_timestamps_require_explicit_offset(stamp):
    assert task_dispatch.route_verdict(receipt(generated_at=stamp), now=NOW) == "MISSING-EVIDENCE"


@pytest.mark.parametrize("stamp", ["2026-10-08T12:00:00Z", "2026-10-08T14:00:00+02:00"])
def test_explicit_offsets_are_normalized(stamp):
    assert task_dispatch.route_verdict(receipt(generated_at=stamp), now=NOW) == "READY"


@pytest.mark.parametrize("field", sorted(task_dispatch.REQUIRED_ROUTE_CHECKS))
def test_route_evidence_requires_every_dispatch_check(field):
    row = receipt()
    del row["checks"][field]
    assert task_dispatch.route_verdict(row, now=NOW) == "MISSING-EVIDENCE"


def test_missing_stale_future_blocked_and_failed_controls():
    for row, wanted in (
        (None, "MISSING-EVIDENCE"),
        (receipt(generated_at=(NOW - timedelta(hours=25)).isoformat()), "STALE-EVIDENCE"),
        (receipt(generated_at=(NOW + timedelta(hours=1)).isoformat()), "MISSING-EVIDENCE"),
        (receipt(status="blocked"), "BLOCKED"),
        (receipt(status="failed"), "NOT-READY"),
    ):
        assert task_dispatch.route_verdict(row, now=NOW) == wanted


def test_loader_preserves_provider_identity_and_rejects_duplicates(tmp_path):
    registry = synthetic_registry(2)
    evidence = complete_evidence(registry)
    for index, row in enumerate(evidence.values()):
        (tmp_path / f"receipt-{index}.yaml").write_text(yaml.safe_dump(row))
    (tmp_path / "legacy.yaml").write_text(yaml.safe_dump({"source": "role-0", "target": "role-1"}))
    assert task_dispatch.load_route_evidence_dir(tmp_path) == evidence
    key, row = next(iter(evidence.items()))
    (tmp_path / "duplicate.yml").write_text(yaml.safe_dump(row))
    loaded = task_dispatch.load_route_evidence_dir(tmp_path)
    assert key not in loaded


def test_registry_order_and_prefix_specific_helper():
    registry = synthetic_registry(3)
    registry = dict(reversed(list(registry.items())))
    assert [r.machine for r in task_dispatch.dispatch_records(registry)] == list(registry)
    assert task_dispatch.find_client_prefix_markers(registry) == []
    registry["role-0"]["task_dispatch"]["ssh_alias"] = "client-example"
    assert task_dispatch.find_client_prefix_markers(registry) == ["role-0:client-example"]


def test_collector_dispatch_block_uses_collecting_source(tmp_path):
    registry = synthetic_registry(3)
    config = tmp_path / "config" / "workstations"
    config.mkdir(parents=True)
    (config / "registry.yaml").write_text(yaml.safe_dump({"machines": registry}))
    state = tmp_path / ".claude" / "state" / "task-dispatch"
    state.mkdir(parents=True)
    evidence = complete_evidence(registry)
    for index, (key, row) in enumerate(evidence.items()):
        if key[0] == "role-0":
            row = copy.deepcopy(row)
            row["generated_at"] = datetime.now(UTC).isoformat()
            (state / f"receipt-{index}.yaml").write_text(yaml.safe_dump(row))
    (tmp_path / "src").symlink_to(REPO_ROOT / "src", target_is_directory=True)
    collector = (REPO_ROOT / "scripts" / "readiness" / "collect-equality.sh").read_text()
    dispatch_block = collector.split("td_json=", 1)[1]
    assert '\"$WS\" \"$MACHINE\" <<' in dispatch_block.splitlines()[0]
    block = dispatch_block.split("<<'PY'", 1)[1].split("\n", 1)[1].split("\nPY\n", 1)[0]
    result = subprocess.run([sys.executable, "-", str(tmp_path), "role-0"], input=block,
                            text=True, capture_output=True, check=True)
    summary = json.loads(result.stdout)
    assert summary["status"] == "ready"
    assert summary["ready_routes"] == summary["total_routes"] == 2
