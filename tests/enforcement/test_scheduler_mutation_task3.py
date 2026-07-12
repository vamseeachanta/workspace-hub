"""RED contract tests for #3475 scheduler-mutation governance closeout."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/enforcement/check-scheduler-mutation-surfaces.py"
REGISTRY = ROOT / "config/scheduled-tasks/mutation-surfaces.yaml"
INVENTORY = ROOT / "docs/reports/issue-3475-command-identity-inventory.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("task3_scheduler_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def current_contract():
    checker = load_checker()
    records = checker.read_index_records(ROOT)
    registry = yaml.safe_load(records[checker.REGISTRY])
    discovered = checker.discover_mutation_surfaces(records)
    return checker, records, registry, discovered


def by_path(registry):
    return {row["path"]: row for row in registry["surfaces"]}


def test_cron_authority_is_exact_and_3475_is_resolved():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []

    rows = by_path(registry)
    cron = rows["scripts/cron/cron_apply.py"]
    assert "disposition_group" not in cron
    operation = cron["operations"][0]
    assert operation["authority_branches"] == [
        {
            "id": "canonical-exact-line",
            "mechanism": "canonical-exact-line",
            "config_source": "config/scheduled-tasks/schedule-tasks.yaml",
            "destructive": True,
            "strength": "exact",
        },
        {
            "id": "legacy-exact-line",
            "mechanism": "legacy-exact-line",
            "config_source": "docs/reports/issue-3475-command-identity-inventory.json",
            "destructive": True,
            "strength": "exact",
        },
    ]
    assert set(operation["transaction"].values()) == {True}
    assert {
        "python-postwrite-exact-state-v1",
        "python-rollback-exact-baseline-v1",
        "cron-canonical-legacy-exact-authority-v1",
    } <= set(operation["attestations"])

    inventory_digest = json.loads(INVENTORY.read_text())["input_digest"]
    assert registry["resolved_dispositions"] == [
        {
            "issue": 3475,
            "members": [
                "scripts/cron/cron_apply.py",
                "scripts/cron/setup-cron.sh",
                "scripts/setup/new-machine-setup.sh",
            ],
            "resolved_on": "2026-07-12",
            "pull_request": 3492,
            "source_digest": inventory_digest,
        }
    ]
    assert {group["issue"]["number"] for group in registry["disposition_groups"]} == {
        3476, 3477, 3478, 3479
    }


def test_transitive_surfaces_are_closed_delegations_with_visible_gaps():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []
    rows = by_path(registry)

    for path in (
        "scripts/cron/setup-cron.sh",
        "scripts/setup/new-machine-setup.sh",
        "scripts/cron/harness-update.sh",
    ):
        row = rows[path]
        assert set(row) <= {"path", "kind", "delegation", "disposition_group"}
        delegation = row["delegation"]
        assert set(delegation) == {"immediate_callee", "terminal", "modes"}
        assert delegation["terminal"] == {
            "path": "scripts/cron/cron_apply.py",
            "operation": "reconcile-current-user-crontab",
        }
        assert delegation["modes"]
        for mode in delegation["modes"]:
            assert set(mode) == {
                "id", "mutation_mode", "args", "target", "exit", "source_attestation"
            }

    assert result.statuses["scripts/cron/setup-cron.sh"] == "compliant"
    assert result.statuses["scripts/setup/new-machine-setup.sh"] == "compliant"
    assert result.statuses["scripts/cron/harness-update.sh"] == "migration-required"
    new_modes = rows["scripts/setup/new-machine-setup.sh"]["delegation"]["modes"]
    assert any(mode["exit"] == "swallow-3490" for mode in new_modes)
    harness_modes = rows["scripts/cron/harness-update.sh"]["delegation"]["modes"]
    assert any(mode["exit"] == "swallow-3479" for mode in harness_modes)


def test_delegation_validation_fails_closed_for_broken_graphs():
    checker, records, registry, discovered = current_contract()

    cases = []
    cycle = copy.deepcopy(registry)
    by_path(cycle)["scripts/cron/setup-cron.sh"]["delegation"]["immediate_callee"] = (
        "scripts/setup/new-machine-setup.sh"
    )
    cases.append((cycle, "cycle"))

    missing = copy.deepcopy(registry)
    by_path(missing)["scripts/cron/setup-cron.sh"]["delegation"]["terminal"]["path"] = (
        "scripts/cron/missing.py"
    )
    cases.append((missing, "terminal"))

    wrong_operation = copy.deepcopy(registry)
    by_path(wrong_operation)["scripts/cron/setup-cron.sh"]["delegation"]["terminal"][
        "operation"
    ] = "not-an-operation"
    cases.append((wrong_operation, "operation"))

    wrong_edge = copy.deepcopy(registry)
    by_path(wrong_edge)["scripts/cron/setup-cron.sh"]["delegation"]["immediate_callee"] = (
        "scripts/cron/harness-update.sh"
    )
    cases.append((wrong_edge, "immediate callee"))

    for candidate, expected in cases:
        result = checker.validate_registry(candidate, discovered, records)
        assert any(expected in error.lower() for error in result.errors), result.errors


def test_direct_primitive_wrapper_cannot_inherit_terminal_compliance():
    checker, records, registry, _ = current_contract()
    records[b"scripts/cron/setup-cron.sh"] += b"\nprintf x | crontab -\n"
    discovered = checker.discover_mutation_surfaces(records)
    result = checker.validate_registry(registry, discovered, records)
    assert any("direct primitive" in error.lower() for error in result.errors)


def test_state_classes_inventory_and_workflow_are_fail_closed():
    checker, records, registry, discovered = current_contract()
    workflow = records[b".github/workflows/enforcement-gate.yml"].decode()
    assert "build-cron-identity-inventory.py --check" in workflow
    inventory_line = next(
        line for line in workflow.splitlines() if "build-cron-identity-inventory.py --check" in line
    )
    assert "|| true" not in inventory_line

    stale = copy.deepcopy(records)
    stale[b"docs/reports/issue-3475-command-identity-inventory.json"] += b" "
    result = checker.validate_registry(registry, discovered, stale)
    assert any("identity inventory" in error.lower() for error in result.errors)

    invalid = copy.deepcopy(records)
    invalid[b"config/workstations/harness-state-classes.yaml"] = (
        b"preserved_external: not-a-list\npreserved_local: []\n"
    )
    result = checker.validate_registry(registry, discovered, invalid)
    assert any("state class" in error.lower() for error in result.errors)


def test_renderer_supports_delegate_rows_and_preserves_migration_issues():
    checker, records, registry, discovered = current_contract()
    result = checker.validate_registry(registry, discovered, records)
    assert result.errors == []
    rendered = checker.render_html(registry, discovered, result, "a" * 64).decode()
    assert "canonical-exact-line" in rendered
    assert "legacy-exact-line" in rendered
    assert "swallow-3490" in rendered
    assert "swallow-3479" in rendered
    for issue in (3476, 3477, 3478, 3479):
        assert f"#{issue}" in rendered
    assert "active disposition: #3475" not in rendered
