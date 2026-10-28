#!/usr/bin/env python3
"""Build/check the deterministic exact cron identity inventory for #3475."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CRON_DIR = Path(__file__).resolve().parent
if str(CRON_DIR) not in sys.path:
    sys.path.insert(0, str(CRON_DIR))

from cron_identity import (  # noqa: E402
    build_ownership_context,
    validate_inventory_inputs,
    validate_state_classes,
)

DEFAULT_CATALOG = ROOT / "config/scheduled-tasks/schedule-tasks.yaml"
DEFAULT_REGISTRY = ROOT / "config/workstations/registry.yaml"
DEFAULT_CLASSES = ROOT / "config/workstations/harness-state-classes.yaml"
DEFAULT_OUTPUT = ROOT / "docs/reports/issue-3475-command-identity-inventory.json"
SOURCE_PATHS = (
    Path(__file__).resolve(),
    ROOT / "scripts/cron/cron_render.py",
    ROOT / "scripts/cron/cron_transaction.py",
    ROOT / "scripts/cron/cron_line_model.py",
    ROOT / "scripts/cron/cron_identity.py",
)


def digest_logical_name(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def input_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    digest.update(b"cron-identity-input-v1\0")
    logical = []
    for path in paths:
        logical.append((digest_logical_name(path), path))
    for name_text, path in sorted(logical):
        name = name_text.encode("utf-8")
        body = path.read_bytes()
        digest.update(struct.pack(">Q", len(name)))
        digest.update(name)
        digest.update(struct.pack(">Q", len(body)))
        digest.update(body)
    return digest.hexdigest()


def build(catalog_path: Path, registry_path: Path, classes_path: Path) -> dict:
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    structure_errors = validate_inventory_inputs(catalog, registry)
    tasks = catalog.get("tasks") if isinstance(catalog, dict) else []
    task_ids = {task.get("id") for task in tasks or [] if isinstance(task, dict)}
    schema_errors = structure_errors + validate_state_classes(classes, task_ids)
    if schema_errors:
        raise ValueError("; ".join(schema_errors))
    machines = sorted(
        machine_id for machine_id, row in (registry.get("machines") or {}).items()
        if row.get("os") == "linux"
    )
    rows, unsupported, collisions = [], [], []
    bound_legacy: set[tuple[str, str]] = set()
    for machine_id in machines:
        _build_machine(
            catalog, registry, classes, machine_id, rows, unsupported,
            collisions, bound_legacy,
        )
    declared_legacy = {
        (row["catalog_task_id"], variant["id"])
        for group in ("preserved_external", "preserved_local")
        for row in classes.get(group) or [] if row.get("catalog_task_id")
        for variant in row.get("legacy_exact_lines") or []
    }
    for task_id, variant_id in sorted(declared_legacy - bound_legacy):
        unsupported.append({"task_id": task_id, "variant_id": variant_id,
                            "error": "legacy variant is not bound in a canonical Linux context"})
    union = [catalog_path, registry_path, classes_path, *SOURCE_PATHS]
    return _public_inventory({
        "schema_version": 1, "input_digest": input_digest(union),
        "machines": machines, "identities": rows,
        "unsupported": unsupported, "collisions": collisions,
    }, registry)


def _opaque_key(kind: str, value: str) -> str:
    """Return a selected display format, not an authentication identifier.

    SHA-256 is defined by FIPS 180-4 (August 2015), section 6.2, SHA-256:
    https://doi.org/10.6028/NIST.FIPS.180-4
    The format selects 12 lowercase hex characters (48 bits) from the digest
    of UTF-8 `cron-{kind}:{value}`, without a trailing newline. Truncation and
    domain labels are application choices, not requirements of the standard.
    For each of machine, task and legacy independently, the design envelope
    is at most 1,000 distinct values per inventory, with accidental-collision
    probability below 1e-8 (pair-count bound n*(n-1)/(2*2**48), assuming uniform
    outputs). This envelope is a sizing assumption, not an enforced count cap.
    Acceptance permits zero observed collisions: projection rejects distinct
    values sharing a key within any kind, including unsupported references.
    A collision requires a versioned format change and inventory regeneration;
    never resolve it by order-dependent suffixes. Cross-kind equality is allowed
    because field names identify the kind. These keys do not conceal guessable
    inputs, and the probability bound does not cover adversarial selection.
    """
    return hashlib.sha256(f"cron-{kind}:{value}".encode("utf-8")).hexdigest()[:12]


def _public_inventory(payload: dict, registry: dict) -> dict:
    """Project only after canonical ownership, legacy binding and collisions."""
    machines = registry["machines"]
    keys = {key: _opaque_key("machine", key) for key in machines}
    if len(set(keys.values())) != len(keys):
        raise ValueError("opaque machine key collision")
    labels = {}
    for key, machine in machines.items():
        for label in [key, machine.get("hostname"), *(machine.get("hostname_aliases") or [])]:
            if label:
                labels[label] = keys[key]
    pattern = re.compile("|".join(re.escape(label) for label in
                                  sorted(labels, key=lambda label: (-len(label), label))))
    kinds = {"task_id": "task", "task_ids": "task",
             "variant_id": "legacy", "legacy_variant_ids": "legacy"}

    seen = {kind: {} for kind in ("machine", "task", "legacy")}

    def checked_key(kind, value):
        key = _opaque_key(kind, value)
        previous = seen[kind].setdefault(key, value)
        if previous != value:
            raise ValueError(f"opaque {kind} key collision")
        return key

    def project(value, field=""):
        if isinstance(value, dict):
            return {key: project(item, key) for key, item in value.items()}
        if isinstance(value, list):
            return [project(item, field) for item in value]
        if isinstance(value, str):
            if field in {"machines", "machine_id"}:
                return keys[value]
            if field in kinds:
                return checked_key(kinds[field], value)
            if field == "error":
                return pattern.sub(lambda match: labels[match.group()], value)
        return value

    return project(payload)


def _build_machine(catalog, registry, classes, machine_id, rows, unsupported,
                   collisions, bound_legacy):
    workspace_root = (registry.get("machines") or {}).get(machine_id, {}).get(
        "workspace_root"
    )
    try:
        context = build_ownership_context(
            catalog, registry, classes, machine_id,
            workspace_hub=workspace_root or "/", fail_on_collision=False,
        )
    except (KeyError, TypeError, ValueError) as exc:
        unsupported.append({"machine_id": machine_id, "error": str(exc)})
        return
    if context["selected_tasks"] and not workspace_root:
        unsupported.append({
            "machine_id": machine_id,
            "error": "selected cron tasks require registry workspace_root",
        })
        return
    collision_lines = {item["line"] for item in context["identity_collisions"]}
    for collision in context["identity_collisions"]:
        collisions.append({
            "machine_id": machine_id, "task_ids": collision["task_ids"],
            "line_sha256": hashlib.sha256(collision["line"].encode()).hexdigest(),
        })
    for task_id, lines in sorted(context["canonical_exact_lines"].items()):
        variants = [item["id"] for item in context["legacy_exact_lines"].get(task_id, [])]
        bound_legacy.update((task_id, variant) for variant in variants)
        for line in lines:
            rows.append({
                "canonical_line_sha256": hashlib.sha256(line.encode()).hexdigest(),
                "legacy_variant_ids": sorted(variants), "machine_id": machine_id,
                "task_id": task_id, "unique": line not in collision_lines,
            })


def render(payload: dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


def rendered_input_digest(raw: bytes) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return "<invalid-json>"
    return str(payload.get("input_digest", "<missing>"))


def inventory_mismatch_summary(current: bytes, generated: bytes) -> str:
    try:
        current_payload = json.loads(current)
        generated_payload = json.loads(generated)
    except json.JSONDecodeError:
        return "inventory body mismatch: current file is not valid JSON"
    for key in ("schema_version", "input_digest", "machines", "unsupported", "collisions"):
        if current_payload.get(key) != generated_payload.get(key):
            return f"inventory body mismatch at {key}"
    current_rows = current_payload.get("identities", [])
    generated_rows = generated_payload.get("identities", [])
    if len(current_rows) != len(generated_rows):
        return (
            "inventory body mismatch: identity row count "
            f"{len(current_rows)} != {len(generated_rows)}"
        )
    for index, (current_row, generated_row) in enumerate(zip(current_rows, generated_rows)):
        if current_row != generated_row:
            return f"inventory body mismatch at identities[{index}]"
    return "inventory body mismatch: bytes differ after canonical JSON comparison"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--state-classes", type=Path, default=DEFAULT_CLASSES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        payload = build(args.catalog, args.registry, args.state_classes)
        generated = render(payload)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    invalid = bool(payload["unsupported"] or payload["collisions"])
    if args.check:
        current = args.output.read_bytes() if args.output.is_file() else b""
        stale = current != generated
        if stale:
            print(f"ERROR: stale identity inventory: {args.output.as_posix()}", file=sys.stderr)
            print(
                "ERROR: expected input_digest "
                f"{payload['input_digest']} but found {rendered_input_digest(current)}",
                file=sys.stderr,
            )
            print(f"ERROR: {inventory_mismatch_summary(current, generated)}", file=sys.stderr)
        return 1 if stale or invalid else 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generated)
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
