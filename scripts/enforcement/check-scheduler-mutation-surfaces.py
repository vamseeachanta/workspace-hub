#!/usr/bin/env python3
"""Validate the index-backed scheduler mutation surface registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = b"config/scheduled-tasks/mutation-surfaces.yaml"
FORENSIC_PATHS = {
    b"scripts/enforcement/check-scheduler-mutation-surfaces.py",
    b"tests/enforcement/test_scheduler_mutation_surfaces.py",
}
FORENSIC_SENTINEL = b"scheduler-mutation-forensic"
DIRECT_PATTERNS = (
    re.compile(rb"(?:^|[|;(&\s])crontab[ \t]+-(?:[ \t]|$)"),  # scheduler-mutation-forensic
    re.compile(rb"\[[ \t]*[\"']crontab[\"'][ \t]*,[ \t]*[\"']-[\"']"),  # scheduler-mutation-forensic
    re.compile(rb"\b(?:Register|Unregister|Set)-ScheduledTask\b"),  # scheduler-mutation-forensic
    re.compile(rb"(?:systemctl[ \t]+--user|run_systemctl)[ \t]+(?:enable|disable)\b"),  # scheduler-mutation-forensic
)
CALLEE_PATHS = (
    b"scripts/cron/cron_apply.py",
    b"scripts/cron/setup-cron.sh",
)
TRANSACTION_FIELDS = (
    "lock",
    "baseline_snapshot",
    "backup",
    "pre_write_cas",
    "post_write_preservation_verify",
    "post_write_exact_state_verify",
    "rollback_cas",
)
TARGET_KINDS = {
    "current-user-cron",
    "root-cron",
    "systemd-user",
    "windows-current-user-task",
}
PRIMITIVES = {
    "crontab-replace",
    "systemd-user-unit-write",
    "systemd-user-enable-disable",
    "windows-task-set",
    "windows-task-unregister-register",
}
AUTHORITY_MECHANISMS = {
    "managed-block-exact",
    "exact-sentinel",
    "command-tokens-adjacent",
    "command-substring",
    "catalog-key-substring",
    "fixed-task-path-name",
    "unknown",
}
ATTESTATIONS = {
    "python-physical-host-equality-guard-v1": (b"scripts/cron/cron_apply.py", b"refusing local crontab reconciliation"),
    "python-prewrite-baseline-cas-v1": (b"scripts/cron/cron_apply.py", b"if current != A"),
    "python-postwrite-preservation-multiset-v1": (b"scripts/cron/cron_apply.py", b"after_counts = Counter"),
    "python-rollback-after-cas-v1": (b"scripts/cron/cron_apply.py", b"if current != after"),
    "cron-command-tokens-adjacent-v1": (b"scripts/cron/cron_transaction.py", b'"command_tokens"'),
    "managed-block-exact-v1": (b"scripts/cron/cron_transaction.py", b"split_managed_block"),
    "shell-exact-sentinel-v1": (b"scripts/install/setup-kanban-loader-timer.sh", b"grep -vF \"$CRON_SENTINEL\""),
    "crontab-current-user-target-v1": (b"scripts/cron/cron_apply.py", b'["crontab", "-"]'),  # scheduler-mutation-forensic
    "crontab-root-target-v1": (b"scripts/setup/setup-engineering-update-cron.sh", b"EUID -ne 0"),
    "systemd-user-unit-name-v1": (b"scripts/install/setup-kanban-loader-timer.sh", b'UNIT_NAME="kanban-loader-sync"'),
    "systemd-user-enable-disable-v1": (b"scripts/install/setup-kanban-loader-timer.sh", b'run_systemctl enable --now "${UNIT_NAME}.timer"'),  # scheduler-mutation-forensic
    "windows-task-path-name-v1": (b"scripts/windows/setup-scheduler-tasks.ps1", b'$TaskPath = "\\Claude\\"'),
    "windows-current-user-principal-v1": (b"scripts/windows/setup-scheduler-tasks.ps1", b"-UserId $env:USERNAME"),
    "windows-task-set-operation-v1": (b"scripts/solver/setup-scheduler.ps1", b"Set-ScheduledTask -TaskName"),  # scheduler-mutation-forensic
    "windows-task-unregister-register-v1": (b"scripts/windows/setup-scheduler-tasks.ps1", b"Unregister-ScheduledTask -TaskName"),  # scheduler-mutation-forensic
}


class GitTransportError(RuntimeError):
    pass


@dataclass(frozen=True)
class Discovery:
    direct: set[str]
    transitive: set[str]
    edges: set[tuple[str, str]]


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    statuses: dict[str, str]


def _display(path: bytes) -> str:
    return path.decode("utf-8", "surrogateescape")


def read_index_records(repo: Path, git_command: str = "git") -> dict[bytes, bytes]:
    listed = subprocess.run(
        [git_command, "ls-files", "-z"], cwd=repo, capture_output=True, check=False
    )
    if listed.returncode:
        raise GitTransportError("git ls-files -z failed")
    paths = [path for path in listed.stdout.split(b"\0") if path]
    commands = b"".join(b"contents :" + path + b"\0" for path in paths)
    read = subprocess.run(
        [git_command, "cat-file", "--batch-command", "-Z"],
        cwd=repo,
        input=commands,
        capture_output=True,
        check=False,
    )
    if read.returncode:
        raise GitTransportError(
            "Git with cat-file --batch-command -Z support is required (minimum Git 2.41)"
        )
    records: dict[bytes, bytes] = {}
    offset = 0
    for path in paths:
        end = read.stdout.find(b"\0", offset)
        if end < 0:
            raise GitTransportError("truncated NUL-mode cat-file header")
        header = read.stdout[offset:end]
        offset = end + 1
        parts = header.rsplit(b" ", 2)
        if len(parts) != 3 or parts[1] != b"blob":
            raise GitTransportError(f"index object unavailable for {_display(path)}")
        size = int(parts[2])
        blob = read.stdout[offset : offset + size]
        offset += size
        if len(blob) != size or read.stdout[offset : offset + 1] != b"\0":
            raise GitTransportError("truncated NUL-mode cat-file content")
        offset += 1
        records[path] = blob
    return records


def discover_mutation_surfaces(records: dict[bytes, bytes]) -> Discovery:
    direct: set[str] = set()
    transitive: set[str] = set()
    edges: set[tuple[str, str]] = set()
    for raw_path, body in records.items():
        if not raw_path.startswith(b"scripts/") or not raw_path.endswith((b".sh", b".py", b".ps1")):
            continue
        path = _display(raw_path)
        for line in body.splitlines():
            if line.lstrip().startswith(b"#"):
                continue
            suppressed = raw_path in FORENSIC_PATHS and FORENSIC_SENTINEL in line
            if not suppressed and any(pattern.search(line) for pattern in DIRECT_PATTERNS):
                direct.add(path)
        if raw_path in FORENSIC_PATHS:
            continue
        executable = b"\n".join(
            line for line in body.splitlines() if not line.lstrip().startswith(b"#")
        )
        for callee in CALLEE_PATHS:
            literal_call = re.search(
                rb"(?m)^[ \t]*(?:[A-Za-z_][A-Za-z0-9_]*=\$\()?[ \t]*bash[ \t]+[^\n]*"
                + re.escape(callee),
                executable,
            )
            known_constant_call = (
                raw_path == b"scripts/cron/harness-update.sh"
                and callee == b"scripts/cron/setup-cron.sh"
                and b'bash "$installer"' in executable
            )
            reviewed_advisory_edge = (
                raw_path == b"scripts/cron/setup-cron.sh"
                and callee == b"scripts/cron/cron_apply.py"
                and callee in executable
            )
            if raw_path != callee and (literal_call or known_constant_call or reviewed_advisory_edge):
                transitive.add(path)
                edges.add((path, _display(callee)))
    return Discovery(direct, transitive, edges)


def derive_status(
    branches: list[dict[str, Any]],
    attestations: list[bool],
    required_transactions: list[bool],
) -> str:
    weak = any(
        branch.get("destructive")
        and branch.get("strength") in {"substring", "unknown"}
        for branch in branches
    )
    return "migration-required" if weak or not all(attestations) or not all(required_transactions) else "compliant"


def input_digest(registry_bytes: bytes, records: dict[bytes, bytes]) -> str:
    framed = bytearray(b"scheduler-mutation-input-v1\0")
    framed.extend(struct.pack(">Q", len(registry_bytes)))
    framed.extend(registry_bytes)
    framed.extend(struct.pack(">Q", len(records)))
    for path, blob in sorted(records.items()):
        framed.extend(struct.pack(">Q", len(path)))
        framed.extend(path)
        framed.extend(struct.pack(">Q", len(blob)))
        framed.extend(blob)
    return hashlib.sha256(framed).hexdigest()


def _attest(attestation: str, records: dict[bytes, bytes], operation_path: bytes) -> bool:
    if attestation == "python-postwrite-exact-state-v1":
        return False
    if attestation == "cron-classifier-destructive-branches-v1":
        body = records.get(b"scripts/cron/cron_transaction.py", b"")
        return all(token in body for token in (b"installed_fingerprint", b"catalog_key", b"command_tokens"))
    if attestation == "kanban-backend-operation-set-v1":
        body = records.get(operation_path, b"")
        return all(token in body for token in (b"write_unit", b"enable --now", b"run_crontab -"))
    expected = ATTESTATIONS.get(attestation)
    if not expected:
        return False
    source, token = expected
    return token in records.get(source, b"")


def validate_registry(
    registry: dict[str, Any], discovery: Discovery, records: dict[bytes, bytes]
) -> ValidationResult:
    errors: list[str] = []
    statuses: dict[str, str] = {}
    if set(registry or {}) != {"schema_version", "surfaces", "disposition_groups"}:
        errors.append("registry top-level keys must be closed")
        return ValidationResult(errors, statuses)
    if registry["schema_version"] != 1:
        errors.append("schema_version must be 1")
    surfaces = registry.get("surfaces")
    if not isinstance(surfaces, list):
        return ValidationResult(errors + ["surfaces must be a list"], statuses)
    rows: dict[str, dict[str, Any]] = {}
    allowed_surface = {"path", "kind", "operations", "edge", "disposition_group"}
    allowed_operation = {
        "id", "primitive", "target_kind", "scheduler_identity",
        "execution_host_binding", "selection_condition", "destructive",
        "authority_branches", "transaction", "attestations",
    }
    for row in surfaces:
        path = row.get("path", "")
        if path in rows:
            errors.append(f"duplicate surface: {path}")
            continue
        rows[path] = row
        if set(row) - allowed_surface or row.get("computed_status") is not None:
            errors.append(f"{path}: unknown/authored status field")
        if row.get("kind") not in {"direct-owner", "transitive-entrypoint"}:
            errors.append(f"{path}: invalid kind")
        if path.encode() not in records:
            errors.append(f"{path}: path is not tracked")
        operations = row.get("operations")
        if not isinstance(operations, list) or not operations:
            errors.append(f"{path}: operations required")
            continue
        row_branches: list[dict[str, Any]] = []
        row_attestations: list[bool] = []
        row_transactions: list[bool] = []
        operation_ids: set[str] = set()
        for operation in operations:
            if set(operation) - allowed_operation:
                errors.append(f"{path}: unknown operation key")
            operation_ids.add(operation.get("id", ""))
            if operation.get("primitive") not in PRIMITIVES:
                errors.append(f"{path}: invalid primitive")
            if operation.get("target_kind") not in TARGET_KINDS:
                errors.append(f"{path}: exact target_kind required")
            if operation.get("execution_host_binding") not in {"physical-local", "explicit-remote-transport"}:
                errors.append(f"{path}: exact execution_host_binding required")
            if not operation.get("scheduler_identity"):
                errors.append(f"{path}: scheduler_identity required")
            branches = operation.get("authority_branches", [])
            if not branches:
                errors.append(f"{path}: authority_branches required")
            for branch in branches:
                required = {"id", "mechanism", "config_source", "destructive", "strength"}
                if set(branch) != required or branch.get("mechanism") not in AUTHORITY_MECHANISMS:
                    errors.append(f"{path}: invalid authority branch")
                if branch.get("strength") not in {"exact", "parsed", "substring", "unknown"}:
                    errors.append(f"{path}: invalid authority strength")
                row_branches.append(branch)
            transaction = operation.get("transaction", {})
            if set(transaction) != set(TRANSACTION_FIELDS):
                errors.append(f"{path}: complete transaction contract required")
            row_transactions.extend(bool(transaction.get(field)) for field in TRANSACTION_FIELDS)
            for attestation in operation.get("attestations", []):
                passed = _attest(attestation, records, path.encode())
                row_attestations.append(passed)
                if not passed and transaction.get("post_write_exact_state_verify"):
                    errors.append(f"{path}: attestation failed: {attestation}")
        if path == "scripts/install/setup-kanban-loader-timer.sh" and operation_ids != {
            "systemd-unit-write", "systemd-enable-disable", "crontab-replace"
        }:
            errors.append(f"{path}: incomplete backend operation set")
        status = derive_status(row_branches, row_attestations or [False], row_transactions)
        statuses[path] = status
    registered_direct = {path for path, row in rows.items() if row.get("kind") == "direct-owner"}
    registered_transitive = {path for path, row in rows.items() if row.get("kind") == "transitive-entrypoint"}
    for path in sorted(discovery.direct ^ registered_direct):
        errors.append(f"direct inventory mismatch: {path}")
    for path in sorted(discovery.transitive ^ registered_transitive):
        errors.append(f"transitive inventory mismatch: {path}")
    for path, row in rows.items():
        if row.get("kind") == "transitive-entrypoint":
            edge = row.get("edge", {})
            pair = (path, edge.get("callee", ""))
            if pair not in discovery.edges or edge.get("call_form") not in {
                "literal-exec", "literal-bash", "constant-path-exec"
            } or edge.get("mutation_mode") not in {"default", "flag-gated"}:
                errors.append(f"{path}: invalid or undiscovered transitive edge")
    migration_paths = {path for path, status in statuses.items() if status == "migration-required"}
    covered: set[str] = set()
    for group in registry.get("disposition_groups", []):
        if set(group) != {"group_id", "issue", "members", "defect_class"}:
            errors.append("invalid disposition group keys")
            continue
        issue = group.get("issue", {})
        if set(issue) != {"repository", "number"} or issue.get("repository") != "vamseeachanta/workspace-hub" or not isinstance(issue.get("number"), int) or issue.get("number") == 3470:
            errors.append(f"{group.get('group_id')}: invalid follow-up coordinate")
        members = set(group.get("members", []))
        if covered & members:
            errors.append(f"{group.get('group_id')}: duplicate disposition member")
        covered |= members
    if covered != migration_paths:
        errors.append("disposition groups must exactly cover migration-required surfaces")
    return ValidationResult(errors, statuses)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        records = read_index_records(REPO_ROOT)
        registry_bytes = records.get(REGISTRY_PATH)
        if registry_bytes is None:
            raise ValueError("tracked registry is missing")
        registry = yaml.safe_load(registry_bytes)
        discovery = discover_mutation_surfaces(records)
        result = validate_registry(registry, discovery, records)
    except (GitTransportError, ValueError, yaml.YAMLError) as exc:
        discovery = Discovery(set(), set(), set())
        result = ValidationResult([str(exc)], {})
    payload = {
        "direct": sorted(discovery.direct),
        "errors": result.errors,
        "status": "ok" if not result.errors else "error",
        "transitive": sorted(discovery.transitive),
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if not result.errors:
            print("scheduler mutation surfaces: OK")
    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
