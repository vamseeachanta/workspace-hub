"""Closed delegation and identity-input governance for scheduler mutations."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

import yaml


EXPECTED_MODES = {
    "scripts/cron/setup-cron.sh": [
        ("default-apply", "destructive", ["--machine=<canonical>", "--apply"], "physical-local", "propagate", "setup-default-apply-v1"),
        ("dry-run", "non-mutating", ["--machine=<canonical>", "--json"], "physical-local", "propagate", "setup-dry-run-v1"),
        ("live-reload", "destructive", ["--machine=<canonical>", "--apply", "--allow-live-reload"], "physical-local", "propagate", "setup-live-reload-v1"),
        ("remote-rejection", "non-mutating", ["--machine=<remote>"], "physical-local", "reject", "setup-remote-reject-v1"),
        ("windows-skip", "non-mutating", ["--machine=<windows>"], "platform-selected", "skip", "setup-windows-skip-v1"),
    ],
    "scripts/setup/new-machine-setup.sh": [
        ("default-linux", "destructive", ["setup-cron"], "physical-local", "propagate", "new-machine-default-v1"),
        ("dry-run-preview", "non-mutating", ["setup-cron", "--dry-run"], "physical-local", "swallow-3490", "new-machine-dry-run-v1"),
        ("windows-skip", "non-mutating", ["setup-cron"], "platform-selected", "swallow-3490", "new-machine-windows-v1"),
    ],
    "scripts/cron/harness-update.sh": [
        ("scheduled-sync", "destructive", ["setup-cron"], "physical-local", "swallow-3479", "harness-default-v1"),
        ("dry-run-sync", "non-mutating", ["setup-cron", "--dry-run"], "physical-local", "swallow-3479", "harness-dry-run-v1"),
    ],
}
MODE_FIELDS = ("id", "mutation_mode", "args", "target", "exit", "source_attestation")


def validate_delegation_schema(path: str, delegation: Any) -> list[str]:
    required = {"immediate_callee", "terminal", "modes"}
    if not isinstance(delegation, dict) or set(delegation) != required:
        return [f"{path}: invalid delegation schema"]
    errors = _validate_terminal(path, delegation.get("terminal"))
    modes = delegation.get("modes")
    if not isinstance(modes, list) or not modes:
        return errors + [f"{path}: delegation modes required"]
    expected = EXPECTED_MODES.get(path)
    actual = [tuple(mode.get(field) for field in MODE_FIELDS) for mode in modes]
    if expected is None or actual != expected:
        errors.append(f"{path}: exact wrapper mode contract mismatch")
    return errors


def _validate_terminal(path: str, terminal: Any) -> list[str]:
    if not isinstance(terminal, dict) or set(terminal) != {"path", "operation"}:
        return [f"{path}: invalid terminal schema"]
    return []


def validate_delegation_graph(rows, statuses, errors):
    for path, row in rows.items():
        if row.get("kind") == "transitive-entrypoint":
            _validate_chain(path, row, rows, statuses, errors)


def _validate_chain(path, row, rows, statuses, errors):
    terminal = row.get("delegation", {}).get("terminal", {})
    current, seen = path, set()
    while rows.get(current, {}).get("kind") == "transitive-entrypoint":
        if current in seen:
            errors.append(f"{path}: delegation cycle")
            return
        seen.add(current)
        current = rows[current].get("delegation", {}).get("immediate_callee", "")
        if current not in rows:
            errors.append(f"{path}: missing delegation target {current}")
            return
    if current != terminal.get("path"):
        errors.append(f"{path}: terminal path does not resolve")
        return
    operations = {op.get("id") for op in rows.get(current, {}).get("operations", [])}
    if terminal.get("operation") not in operations:
        errors.append(f"{path}: terminal operation is missing or ambiguous")
    if statuses.get(current) != "compliant" and not row.get("disposition_group"):
        statuses[path] = "migration-required"


def validate_identity_inputs(root: Path, registry, records, errors):
    try:
        catalog = yaml.safe_load(records[b"config/scheduled-tasks/schedule-tasks.yaml"]) or {}
        classes = yaml.safe_load(records[b"config/workstations/harness-state-classes.yaml"])
        cron_dir = root / "scripts/cron"
        if str(cron_dir) not in sys.path:
            sys.path.insert(0, str(cron_dir))
        from cron_identity import validate_state_classes
        state_errors = validate_state_classes(classes, {task.get("id") for task in catalog.get("tasks") or []})
        errors.extend(f"state class: {error}" for error in state_errors)
        inventory = _validate_inventory_bytes(records, errors)
        _validate_inventory_digest(inventory, records, errors)
        resolved = registry.get("resolved_dispositions", [{}])[0]
        if resolved.get("source_digest") != inventory.get("input_digest"):
            errors.append("resolved #3475 source digest does not match identity inventory")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        errors.append(f"identity inventory/state class validation failed: {exc}")


def _validate_inventory_bytes(records, errors):
    raw = records[b"docs/reports/issue-3475-command-identity-inventory.json"]
    inventory = json.loads(raw)
    canonical = (json.dumps(inventory, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    if raw != canonical:
        errors.append("identity inventory is not canonical/stale")
    return inventory


def _validate_inventory_digest(inventory, records, errors):
    sources = [b"config/scheduled-tasks/schedule-tasks.yaml", b"config/workstations/registry.yaml",
               b"config/workstations/harness-state-classes.yaml", b"scripts/cron/build-cron-identity-inventory.py",
               b"scripts/cron/cron_render.py", b"scripts/cron/cron_transaction.py",
               b"scripts/cron/cron_line_model.py", b"scripts/cron/cron_identity.py",
               b"scripts/lib/git_index_snapshot.py", b"pyproject.toml", b"uv.lock"]
    digest = hashlib.sha256(b"cron-identity-input-v1\0")
    for source in sorted(sources):
        digest.update(struct.pack(">Q", len(source)) + source)
        body = records[source]
        digest.update(struct.pack(">Q", len(body)) + body)
    if inventory.get("input_digest") != digest.hexdigest():
        errors.append("identity inventory input digest is stale")
