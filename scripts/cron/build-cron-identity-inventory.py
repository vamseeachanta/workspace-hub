#!/usr/bin/env python3
"""Build/check the deterministic exact cron identity inventory for #3475."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CRON_DIR = Path(__file__).resolve().parent
if str(CRON_DIR) not in sys.path:
    sys.path.insert(0, str(CRON_DIR))

from cron_identity import build_ownership_context, validate_state_classes  # noqa: E402

DEFAULT_CATALOG = ROOT / "config/scheduled-tasks/schedule-tasks.yaml"
DEFAULT_REGISTRY = ROOT / "config/workstations/registry.yaml"
DEFAULT_CLASSES = ROOT / "config/workstations/harness-state-classes.yaml"
DEFAULT_OUTPUT = ROOT / "docs/reports/issue-3475-command-identity-inventory.json"
SOURCE_PATHS = (
    Path(__file__).resolve(),
    ROOT / "scripts/cron/cron_render.py",
    ROOT / "scripts/cron/cron_transaction.py",
    ROOT / "scripts/cron/cron_identity.py",
)


def input_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    digest.update(b"cron-identity-input-v1\0")
    logical = []
    for path in paths:
        try:
            name = str(path.resolve().relative_to(ROOT.resolve()))
        except ValueError:
            name = path.name
        logical.append((name, path))
    for name_text, path in sorted(logical):
        name = name_text.encode("utf-8")
        body = path.read_bytes()
        digest.update(struct.pack(">Q", len(name)))
        digest.update(name)
        digest.update(struct.pack(">Q", len(body)))
        digest.update(body)
    return digest.hexdigest()


def build(catalog_path: Path, registry_path: Path, classes_path: Path) -> dict:
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    classes = yaml.safe_load(classes_path.read_text(encoding="utf-8"))
    schema_errors = validate_state_classes(
        classes, {task.get("id") for task in catalog.get("tasks") or []}
    )
    if schema_errors:
        raise ValueError("; ".join(schema_errors))
    machines = sorted(
        machine_id for machine_id, row in (registry.get("machines") or {}).items()
        if row.get("os") == "linux"
    )
    rows: list[dict] = []
    unsupported: list[dict] = []
    collisions: list[dict] = []
    bound_legacy: set[tuple[str, str]] = set()
    for machine_id in machines:
        try:
            context = build_ownership_context(
                catalog, registry, classes, machine_id, fail_on_collision=False
            )
        except (KeyError, TypeError, ValueError) as exc:
            unsupported.append({"machine_id": machine_id, "error": str(exc)})
            continue
        collision_lines = {item["line"] for item in context["identity_collisions"]}
        for collision in context["identity_collisions"]:
            collisions.append({
                "machine_id": machine_id,
                "task_ids": collision["task_ids"],
                "line_sha256": hashlib.sha256(
                    collision["line"].encode("utf-8")
                ).hexdigest(),
            })
        for task_id, lines in sorted(context["canonical_exact_lines"].items()):
            for line in lines:
                line_digest = hashlib.sha256(line.encode("utf-8")).hexdigest()
                variants = [item["id"] for item in context["legacy_exact_lines"].get(task_id, [])]
                bound_legacy.update((task_id, variant) for variant in variants)
                rows.append({"canonical_line_sha256": line_digest,
                             "legacy_variant_ids": sorted(variants),
                             "machine_id": machine_id, "task_id": task_id,
                             "unique": line not in collision_lines})
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
    return {"schema_version": 1, "input_digest": input_digest(union),
            "machines": machines, "identities": rows,
            "unsupported": unsupported, "collisions": collisions}


def render(payload: dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


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
        stale = not args.output.is_file() or args.output.read_bytes() != generated
        if stale:
            print(f"ERROR: stale identity inventory: {args.output}", file=sys.stderr)
        return 1 if stale or invalid else 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generated)
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
