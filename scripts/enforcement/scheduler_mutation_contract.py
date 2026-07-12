"""Closed schema and deterministic status/provenance helpers for #3470."""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from typing import Any

from scheduler_mutation_delegation import validate_delegation_schema

TX_FIELDS = (
    "lock",
    "baseline_snapshot",
    "backup",
    "pre_write_cas",
    "post_write_preservation_verify",
    "post_write_exact_state_verify",
    "rollback_cas",
)
TX_ATTEST = {
    "lock": "python-lock-scope-v1",
    "baseline_snapshot": "python-baseline-snapshot-v1",
    "backup": "python-backup-baseline-v1",
    "pre_write_cas": "python-prewrite-cas-v1",
    "post_write_preservation_verify": "python-postwrite-preservation-multiset-v1",
    "post_write_exact_state_verify": "python-postwrite-exact-state-v1",
    "rollback_cas": "python-rollback-after-cas-v1",
}
TARGETS = {"current-user-cron", "root-cron", "systemd-user", "windows-current-user-task"}
MECHANISMS = {
    "canonical-exact-line",
    "legacy-exact-line",
    "managed-block-exact",
    "exact-sentinel",
    "command-tokens-adjacent",
    "command-substring",
    "catalog-key-substring",
    "fixed-task-path-name",
    "unknown",
}
STRENGTHS = {"exact", "parsed", "substring", "unknown"}
SELECTION_CONDITIONS = {
    "systemd-available", "systemd-unavailable",
    "systemd-available-uninstall", "systemd-unavailable-uninstall",
    "remove-mode", "replace-mode",
}
DEFECT_CLASSES = {
    "mixed-destructive-ownership-authority",
    "untransactional-whole-crontab-replacement",
    "untransactional-dual-backend-replacement",
    "windows-task-mutation-without-verified-transaction",
    "transitive-mutation-error-swallowing",
}
DISPOSITION_CONTRACT = {
    "legacy-crontab-writers": (
        3476, "untransactional-whole-crontab-replacement",
        {"scripts/coordination/context/setup_cron.sh", "scripts/operations/maintenance/setup_maintenance_cron.sh", "scripts/setup/setup-engineering-update-cron.sh"},
    ),
    "kanban-dual-backend": (
        3477, "untransactional-dual-backend-replacement",
        {"scripts/install/setup-kanban-loader-timer.sh"},
    ),
    "windows-task-writers": (
        3478, "windows-task-mutation-without-verified-transaction",
        {"scripts/windows/setup-scheduler-tasks.ps1", "scripts/coordination/context/setup_scheduled_task.ps1", "scripts/solver/setup-scheduler.ps1"},
    ),
    "harness-update": (
        3479, "transitive-mutation-error-swallowing",
        {"scripts/cron/harness-update.sh"},
    ),
}
ATT_SOURCES = {
    "python-physical-host-equality-guard-v1": b"scripts/cron/cron_apply.py",
    "shell-physical-host-equality-guard-v1": b"scripts/cron/setup-cron.sh",
    "shell-local-delegation-v1": b"",
    "python-lock-scope-v1": b"scripts/cron/cron_apply.py",
    "python-baseline-snapshot-v1": b"scripts/cron/cron_apply.py",
    "python-backup-baseline-v1": b"scripts/cron/cron_apply.py",
    "python-prewrite-cas-v1": b"scripts/cron/cron_apply.py",
    "python-postwrite-preservation-multiset-v1": b"scripts/cron/cron_transaction.py",
    "python-postwrite-exact-state-v1": b"scripts/cron/cron_apply.py",
    "python-rollback-exact-baseline-v1": b"scripts/cron/cron_apply.py",
    "cron-canonical-legacy-exact-authority-v1": b"scripts/cron/cron_transaction.py",
    "python-rollback-after-cas-v1": b"scripts/cron/cron_apply.py",
    "cron-command-tokens-adjacent-v1": b"scripts/cron/cron_transaction.py",
    "cron-classifier-destructive-branches-v1": b"scripts/cron/cron_transaction.py",
    "shell-exact-sentinel-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "kanban-backend-operation-set-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "crontab-current-user-target-v1": b"scripts/cron/cron_apply.py",
    "crontab-root-target-v1": b"scripts/setup/setup-engineering-update-cron.sh",
    "systemd-user-unit-name-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "systemd-user-enable-disable-v1": b"scripts/install/setup-kanban-loader-timer.sh",
    "windows-task-path-name-v1": b"scripts/windows/setup-scheduler-tasks.ps1",
    "windows-current-user-principal-v1": b"scripts/windows/setup-scheduler-tasks.ps1",
    "windows-task-set-operation-v1": b"scripts/solver/setup-scheduler.ps1",
    "windows-task-unregister-register-v1": b"scripts/windows/setup-scheduler-tasks.ps1",
    "context-windows-principal-v1": b"scripts/coordination/context/setup_scheduled_task.ps1",
    "context-windows-task-path-name-v1": b"scripts/coordination/context/setup_scheduled_task.ps1",
    "solver-windows-task-name-v1": b"scripts/solver/setup-scheduler.ps1",
    "setup-default-apply-v1": b"scripts/cron/setup-cron.sh",
    "setup-dry-run-v1": b"scripts/cron/setup-cron.sh",
    "setup-live-reload-v1": b"scripts/cron/setup-cron.sh",
    "setup-remote-reject-v1": b"scripts/cron/setup-cron.sh",
    "setup-windows-skip-v1": b"scripts/cron/setup-cron.sh",
    "new-machine-default-v1": b"scripts/setup/new-machine-setup.sh",
    "new-machine-dry-run-v1": b"scripts/setup/new-machine-setup.sh",
    "new-machine-windows-v1": b"scripts/setup/new-machine-setup.sh",
    "harness-default-v1": b"scripts/cron/harness-update.sh",
    "harness-dry-run-v1": b"scripts/cron/harness-update.sh",
}


@dataclass(frozen=True)
class Discovery:
    direct: set[str]
    transitive: set[str]
    edges: dict[str, tuple[str, str]]
    primitives: dict[str, set[str]]
    unknown_edges: set[str]


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    statuses: dict[str, str]


def attestation_source(name: str) -> bytes:
    return ATT_SOURCES.get(name, b"")


def derive_status(
    branches: list[dict[str, Any]],
    attestations: list[bool],
    required_transactions: list[bool],
) -> str:
    weak = any(
        branch["destructive"] and branch["strength"] in {"substring", "unknown"}
        for branch in branches
    )
    if weak or not all(attestations) or not all(required_transactions):
        return "migration-required"
    return "compliant"


def input_digest(registry_bytes: bytes, records: dict[bytes, bytes]) -> str:
    data = bytearray(b"scheduler-mutation-input-v1\0")
    data += struct.pack(">Q", len(registry_bytes)) + registry_bytes
    data += struct.pack(">Q", len(records))
    for path, blob in sorted(records.items()):
        data += struct.pack(">Q", len(path)) + path
        data += struct.pack(">Q", len(blob)) + blob
    return hashlib.sha256(data).hexdigest()


def digest_record_union(
    registry: dict[str, Any], records: dict[bytes, bytes]
) -> dict[bytes, bytes]:
    paths = {
        b"scripts/enforcement/check-scheduler-mutation-surfaces.py",
        b"scripts/enforcement/scheduler_mutation_contract.py",
        b"scripts/enforcement/scheduler_mutation_attestations.py",
        b"scripts/enforcement/scheduler_mutation_discovery.py",
        b"scripts/enforcement/scheduler_mutation_delegation.py",
        b"scripts/enforcement/scheduler_mutation_report.py",
        b"scripts/enforcement/scheduler_mutation_wrapper_attestations.py",
        b"tests/enforcement/test_scheduler_mutation_surfaces.py",
        b"tests/enforcement/test_scheduler_mutation_hardening.py",
        b"tests/enforcement/test_scheduler_mutation_delivery.py",
        b".github/workflows/enforcement-gate.yml",
    }
    for row in registry["surfaces"]:
        paths.add(row["path"].encode())
        for operation in row.get("operations", []):
            paths.update(
                branch["config_source"].encode()
                for branch in operation["authority_branches"]
            )
            for name in operation["attestations"]:
                source = attestation_source(name)
                if not source:
                    raise ValueError(f"attestation has no digest source: {name}")
                paths.add(source)
        for mode in row.get("delegation", {}).get("modes", []):
            paths.add(attestation_source(mode["source_attestation"]) or row["path"].encode())
    paths.update({
        b"scripts/cron/build-cron-identity-inventory.py",
        b"scripts/cron/cron_identity.py",
        b"docs/reports/issue-3475-command-identity-inventory.json",
        b"config/workstations/harness-state-classes.yaml",
        b"config/workstations/registry.yaml",
        b"config/scheduled-tasks/schedule-tasks.yaml",
        b"tests/enforcement/test_scheduler_mutation_task3.py",
    })
    missing = paths - records.keys()
    if missing:
        raise KeyError(f"digest source missing: {sorted(missing)!r}")
    return {path: records[path] for path in paths}


def validate_closed_schema(
    registry: dict[str, Any],
    tracked_paths: set[bytes],
    primitives: set[str],
) -> list[str]:
    if set(registry) != {"schema_version", "surfaces", "disposition_groups", "resolved_dispositions"}:
        return ["registry top-level schema is invalid"]
    if registry.get("schema_version") != 2:
        return ["registry schema_version must be 2"]
    errors: list[str] = []
    for row in registry.get("surfaces", []):
        errors.extend(_validate_surface(row, tracked_paths, primitives))
    for group in registry.get("disposition_groups", []):
        errors.extend(_validate_group(group))
    errors.extend(_validate_resolved(registry.get("resolved_dispositions")))
    return errors


def _validate_surface(
    row: dict[str, Any], tracked_paths: set[bytes], primitives: set[str]
) -> list[str]:
    allowed = {"path", "kind", "operations", "delegation", "disposition_group"}
    path = row.get("path", "")
    errors: list[str] = []
    required = {"path", "kind"}
    if not required <= set(row) or set(row) - allowed or row.get("kind") not in {
        "direct-owner",
        "transitive-entrypoint",
    }:
        errors.append(f"{path}: invalid surface schema")
    if path.encode() not in tracked_paths:
        errors.append(f"{path}: path is not tracked")
    if row.get("kind") == "direct-owner":
        operations = row.get("operations")
        if not isinstance(operations, list) or not operations:
            return errors + [f"{path}: operations required"]
        for operation in operations:
            errors.extend(_validate_operation_schema(path, operation, primitives))
        if "delegation" in row:
            errors.append(f"{path}: direct owner cannot declare delegation")
    else:
        if "operations" in row:
            errors.append(f"{path}: transitive surface cannot declare operations")
        errors.extend(validate_delegation_schema(path, row.get("delegation")))
    return errors


def _validate_operation_schema(
    path: str, operation: dict[str, Any], primitives: set[str]
) -> list[str]:
    allowed = {
        "id", "primitive", "target_kind", "scheduler_identity",
        "execution_host_binding", "selection_condition", "destructive",
        "authority_branches", "transaction", "attestations",
    }
    errors: list[str] = []
    required = allowed - {"selection_condition"}
    if not required <= set(operation) or set(operation) - allowed or operation.get("primitive") not in primitives:
        errors.append(f"{path}: invalid operation schema/primitive")
    if operation.get("target_kind") not in TARGETS or not operation.get("scheduler_identity"):
        errors.append(f"{path}: invalid target/scheduler identity")
    if operation.get("execution_host_binding") not in {
        "physical-local",
        "explicit-remote-transport",
    }:
        errors.append(f"{path}: invalid execution-host binding")
    if not isinstance(operation.get("destructive"), bool):
        errors.append(f"{path}: destructive must be boolean")
    selection = operation.get("selection_condition")
    if selection is not None and selection not in SELECTION_CONDITIONS:
        errors.append(f"{path}: invalid selection condition")
    branches = operation.get("authority_branches")
    if not isinstance(branches, list) or not branches:
        errors.append(f"{path}: authority branches required")
    else:
        for branch in branches:
            errors.extend(_validate_branch(path, branch))
    transaction = operation.get("transaction", {})
    if set(transaction) != set(TX_FIELDS) or not all(
        isinstance(value, bool) for value in transaction.values()
    ):
        errors.append(f"{path}: invalid transaction schema")
    if not isinstance(operation.get("attestations"), list):
        errors.append(f"{path}: attestations must be a list")
    return errors


def _validate_branch(path: str, branch: dict[str, Any]) -> list[str]:
    required = {"id", "mechanism", "config_source", "destructive", "strength"}
    errors: list[str] = []
    if set(branch) != required:
        errors.append(f"{path}: invalid/descriptive authority branch")
    if branch.get("mechanism") not in MECHANISMS:
        errors.append(f"{path}: invalid authority mechanism")
    if branch.get("strength") not in STRENGTHS:
        errors.append(f"{path}: invalid authority strength")
    if not isinstance(branch.get("destructive"), bool):
        errors.append(f"{path}: branch destructive must be boolean")
    return errors


def _validate_resolved(rows: Any) -> list[str]:
    if not isinstance(rows, list) or len(rows) != 1:
        return ["resolved dispositions must contain exactly #3475"]
    row = rows[0]
    required = {"issue", "members", "resolved_on", "pull_request", "source_digest"}
    expected_members = ["scripts/cron/cron_apply.py", "scripts/cron/setup-cron.sh", "scripts/setup/new-machine-setup.sh"]
    if set(row) != required or row.get("issue") != 3475 or row.get("members") != expected_members:
        return ["resolved #3475 disposition contract mismatch"]
    if row.get("resolved_on") != "2026-07-12" or row.get("pull_request") != 3492:
        return ["resolved #3475 date/PR mismatch"]
    digest = row.get("source_digest")
    if not isinstance(digest, str) or len(digest) != 64:
        return ["resolved #3475 source digest invalid"]
    return []


def _validate_group(group: dict[str, Any]) -> list[str]:
    required = {"group_id", "issue", "members", "defect_class"}
    errors: list[str] = []
    if set(group) != required or group.get("defect_class") not in DEFECT_CLASSES:
        errors.append("invalid disposition schema/defect class")
    issue = group.get("issue", {})
    if (
        not isinstance(issue, dict)
        or set(issue) != {"repository", "number"}
        or issue.get("repository") != "vamseeachanta/workspace-hub"
        or not isinstance(issue.get("number"), int)
        or issue.get("number") == 3470
    ):
        errors.append(f"{group.get('group_id')}: invalid issue coordinate")
    if not isinstance(group.get("members"), list) or not group.get("members"):
        errors.append(f"{group.get('group_id')}: members required")
    expected = DISPOSITION_CONTRACT.get(group.get("group_id"))
    actual = (issue.get("number"), group.get("defect_class"), set(group.get("members", [])))
    if expected is None or actual != expected:
        errors.append(f"{group.get('group_id')}: disposition contract mismatch")
    return errors


def validate_operation_contract(
    path: str,
    operation: dict[str, Any],
    records: dict[bytes, bytes],
    evaluator: Any,
) -> tuple[list[str], list[dict[str, Any]], list[bool], list[bool]]:
    errors: list[str] = []
    branches = operation["authority_branches"]
    ids = [branch["id"] for branch in branches]
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate authority branch id")
    for branch in branches:
        source = branch["config_source"].encode()
        if source not in records:
            errors.append(f"{path}: config_source is not tracked")
        if branch["id"] == "preserved-promotion" and source != b"config/workstations/harness-state-classes.yaml":
            errors.append(f"{path}: config_source not structurally connected")
    attestations = operation["attestations"]
    transaction = operation["transaction"]
    for field, value in transaction.items():
        needed = TX_ATTEST[field]
        if value and needed not in attestations:
            errors.append(f"{path}: true {field} requires {needed}")
    results: list[bool] = []
    for name in attestations:
        passed = name in ATT_SOURCES and evaluator(name, records, path.encode())
        results.append(passed)
        if not passed:
            errors.append(f"{path}: attestation failed: {name}")
    for branch in branches:
        if branch["destructive"] and branch["strength"] in {"exact", "parsed"}:
            _require_branch_attestation(path, operation, branch, attestations, errors)
    transactions = [transaction[field] for field in TX_FIELDS]
    return errors, branches, results, transactions


def _require_branch_attestation(
    path: str,
    operation: dict[str, Any],
    branch: dict[str, Any],
    attestations: list[str],
    errors: list[str],
) -> None:
    required = {
        "command-tokens-adjacent": {"cron-command-tokens-adjacent-v1"},
        "fixed-task-path-name": {
            "windows-task-path-name-v1",
            "context-windows-task-path-name-v1",
            "solver-windows-task-name-v1",
        },
    }.get(branch["mechanism"], set())
    if branch["mechanism"] == "exact-sentinel":
        required = {
            "crontab-replace": "shell-exact-sentinel-v1",
            "systemd-user-enable-disable": "systemd-user-enable-disable-v1",
            "systemd-user-unit-write": "systemd-user-unit-name-v1",
        }
        required = {required.get(operation["primitive"], "")}
    if required and not required.intersection(attestations):
        errors.append(f"{path}: exact branch requires source attestation")
