"""Exact, parser-free destructive identity for rendered cron lines."""
from __future__ import annotations

from typing import Any

from cron_render import build_context, render_task

STATE_CLASS_KEYS = {"classes", "hooks_known", "preserved_external", "preserved_local"}
PRESERVED_ROW_KEYS = {"owner", "note", "fingerprint", "catalog_task_id", "legacy_exact_lines"}
FINGERPRINT_KEYS = {
    "command_contains", "command_tokens", "cwd_contains", "cwd_basename",
    "script_basename",
}


def _validate_fingerprint(label: str, value: object) -> list[str]:
    if not isinstance(value, dict) or not value:
        return [f"{label}: fingerprint must be a non-empty mapping"]
    errors = []
    unknown = set(value) - FINGERPRINT_KEYS
    if unknown:
        errors.append(f"{label}: unknown fingerprint keys {sorted(unknown)}")
    for key, raw in value.items():
        items = raw if isinstance(raw, list) else [raw]
        if not items or any(not isinstance(item, str) or not item for item in items):
            errors.append(f"{label}: fingerprint.{key} must contain non-empty strings")
    return errors


def _validate_preserved_row(label: str, row: object, task_ids: set[str]) -> list[str]:
    if not isinstance(row, dict):
        return [f"{label} must be a mapping"]
    errors = []
    unknown = set(row) - PRESERVED_ROW_KEYS
    if unknown:
        errors.append(f"{label}: unknown row keys {sorted(unknown)}")
    task_id = row.get("catalog_task_id")
    legacy = row.get("legacy_exact_lines")
    if row.get("fingerprint") is not None:
        errors.extend(_validate_fingerprint(label, row["fingerprint"]))
    if legacy is not None and not task_id:
        errors.append(f"{label}: legacy_exact_lines requires catalog_task_id")
    if task_id:
        if task_id not in task_ids:
            errors.append(f"{label}: unknown catalog_task_id {task_id}")
        if row.get("fingerprint") or not legacy:
            errors.append(f"{label}: catalog_task_id requires legacy_exact_lines without fingerprint")
    errors.extend(_validate_legacy(label, legacy))
    return errors


def _validate_legacy(label: str, legacy: object) -> list[str]:
    if legacy is None:
        return []
    if not isinstance(legacy, list) or not legacy:
        return [f"{label}: legacy_exact_lines must be a non-empty list"]
    errors, seen = [], set()
    for variant in legacy:
        if not isinstance(variant, dict) or set(variant) != {"id", "line"}:
            errors.append(f"{label}: invalid legacy exact-line schema")
            continue
        if not all(isinstance(variant.get(key), str) and variant[key] for key in ("id", "line")):
            errors.append(f"{label}: legacy exact-line values must be non-empty strings")
            continue
        if variant["id"] in seen:
            errors.append(f"{label}: duplicate legacy exact-line id {variant['id']}")
        seen.add(variant["id"])
    return errors


def validate_state_classes(data: object, task_ids: set[str]) -> list[str]:
    """Validate closed legacy promotion rows and preservation-only fingerprints."""
    if not isinstance(data, dict):
        return ["state classes root must be a mapping"]
    errors: list[str] = []
    unknown = set(data) - STATE_CLASS_KEYS
    if unknown:
        errors.append(f"unknown state-class top-level keys {sorted(unknown)}")
    if "classes" in data and not isinstance(data["classes"], dict):
        errors.append("classes must be a mapping")
    if "hooks_known" in data and not isinstance(data["hooks_known"], list):
        errors.append("hooks_known must be a list")
    for group in ("preserved_external", "preserved_local"):
        rows = data.get(group, []) or []
        if not isinstance(rows, list):
            errors.append(f"{group} must be a list")
            continue
        for index, row in enumerate(rows):
            label = f"{group}[{index}]"
            errors.extend(_validate_preserved_row(label, row, task_ids))
    return errors


def validate_inventory_inputs(catalog: object, registry: object) -> list[str]:
    errors = []
    if not isinstance(catalog, dict):
        errors.append("catalog root must be a mapping")
        catalog = {}
    tasks = catalog.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("catalog must contain non-empty tasks list")
        tasks = []
    seen = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be a mapping")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"tasks[{index}] requires non-empty id")
        elif task_id in seen:
            errors.append(f"duplicate task id {task_id}")
        seen.add(task_id)
        if task.get("scheduler", "cron") == "cron":
            for field in ("schedule", "command"):
                if not isinstance(task.get(field), str) or not task[field]:
                    errors.append(f"{task_id or index}: cron task requires {field}")
        for field in ("machines", "roles"):
            if field in task and not isinstance(task[field], list):
                errors.append(f"{task_id or index}: {field} must be a list")
    errors.extend(_validate_registry_root(registry))
    return errors


def _validate_registry_root(registry: object) -> list[str]:
    if not isinstance(registry, dict):
        return ["registry root must be a mapping"]
    machines = registry.get("machines")
    if not isinstance(machines, dict) or not machines:
        return ["registry must contain a canonical Linux machine"]
    linux = []
    errors = []
    for machine_id, row in machines.items():
        if not isinstance(row, dict):
            errors.append(f"machine {machine_id} must be a mapping")
        elif row.get("os") == "linux":
            linux.append(machine_id)
    if not linux:
        errors.append("registry must contain a canonical Linux machine")
    return errors


def _roles(registry: dict, machine_id: str) -> list[str]:
    machine = (registry.get("machines") or {}).get(machine_id, {})
    return ((machine.get("harness_profile") or {}).get("roles")) or []


def _selected(tasks: list[dict], roles: list[str], tokens: set[str]) -> list[dict]:
    role_set = set(roles)
    tokens = {str(token).lower() for token in tokens}
    result: dict[str, dict] = {}
    for task in tasks:
        if task.get("scheduler", "cron") != "cron":
            continue
        role_match = bool(role_set & set(task.get("roles") or []))
        machines = {str(item).lower() for item in task.get("machines") or []}
        machine_match = bool(tokens & machines)
        excluded = role_match and machines and not machine_match
        if excluded and not task.get("roles_authoritative"):
            continue
        if role_match or machine_match:
            result[task["id"]] = task
    return [result[key] for key in sorted(result)]


def build_ownership_context(
    catalog: dict, registry: dict, state_classes: dict, machine_id: str,
    *, workspace_hub: str | None = None, fail_on_collision: bool = True,
) -> dict[str, Any]:
    """Render selected tasks and bind complete canonical and legacy lines."""
    context = build_context(machine_id, registry=registry, workspace_hub=workspace_hub)
    machine_id = context["machine_id"]
    roles = _roles(registry, machine_id)
    rendered = [render_task(task, context) for task in _selected(
        catalog.get("tasks") or [], roles, context["tokens"]
    )]
    canonical: dict[str, list[str]] = {}
    legacy: dict[str, list[dict[str, str]]] = {}
    identities: dict[str, dict[str, str]] = {}
    collisions: list[dict[str, Any]] = []

    for task in rendered:
        canonical[task["id"]] = [task["line"]]
        _bind_identity(
            identities, collisions, task["line"], task["id"],
            "canonical-exact-line", "", fail_on_collision,
        )
    selected_ids = set(canonical)
    groups = (state_classes.get("preserved_external") or []) + (
        state_classes.get("preserved_local") or []
    )
    _bind_legacy(groups, selected_ids, legacy, identities, collisions, fail_on_collision)
    preservation = [dict(row) for row in groups if row.get("fingerprint")]
    for task in rendered:
        if task.get("installed_fingerprint"):
            preservation.append({"owner": "catalog-preservation-only",
                                 "fingerprint": dict(task["installed_fingerprint"])})
    return {"machine_id": machine_id, "roles": roles, "selected_tasks": rendered,
            "selected_task_ids": selected_ids, "canonical_exact_lines": canonical,
            "legacy_exact_lines": legacy, "line_identities": identities,
            "preservation_fingerprints": preservation,
            "identity_collisions": collisions}


def _bind_identity(identities, collisions, line, task_id, source, variant_id, fail):
    if not isinstance(line, str) or not line:
        raise ValueError(f"{task_id}: exact cron line must be non-empty")
    prior = identities.get(line)
    if prior and prior["catalog_task_id"] != task_id:
        collisions.append({
            "line": line,
            "task_ids": sorted([prior["catalog_task_id"], task_id]),
            "sources": sorted([prior["source"], source]),
        })
        if fail:
            raise ValueError(f"exact cron line collision: {task_id}")
        return
    identities[line] = {
        "catalog_task_id": task_id, "source": source, "variant_id": variant_id,
    }


def _bind_legacy(groups, selected_ids, legacy, identities, collisions, fail):
    for row in groups:
        task_id = row.get("catalog_task_id")
        if task_id not in selected_ids:
            continue
        for variant in row.get("legacy_exact_lines") or []:
            legacy.setdefault(task_id, []).append(dict(variant))
            _bind_identity(
                identities, collisions, variant["line"], task_id,
                "legacy-exact-line", variant["id"], fail,
            )
