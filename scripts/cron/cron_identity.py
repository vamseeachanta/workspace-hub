"""Exact, parser-free destructive identity for rendered cron lines."""
from __future__ import annotations

from typing import Any

from cron_render import build_context, render_task


def validate_state_classes(data: object, task_ids: set[str]) -> list[str]:
    """Validate closed legacy promotion rows and preservation-only fingerprints."""
    if not isinstance(data, dict):
        return ["state classes root must be a mapping"]
    errors: list[str] = []
    for group in ("preserved_external", "preserved_local"):
        rows = data.get(group, []) or []
        if not isinstance(rows, list):
            errors.append(f"{group} must be a list")
            continue
        for index, row in enumerate(rows):
            label = f"{group}[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{label} must be a mapping")
                continue
            task_id = row.get("catalog_task_id")
            legacy = row.get("legacy_exact_lines")
            if task_id:
                if task_id not in task_ids:
                    errors.append(f"{label}: unknown catalog_task_id {task_id}")
                if row.get("fingerprint") or not legacy:
                    errors.append(f"{label}: catalog_task_id requires legacy_exact_lines without fingerprint")
            if legacy is not None:
                if not isinstance(legacy, list) or not legacy:
                    errors.append(f"{label}: legacy_exact_lines must be a non-empty list")
                    continue
                seen: set[str] = set()
                for variant in legacy:
                    if not isinstance(variant, dict) or set(variant) != {"id", "line"}:
                        errors.append(f"{label}: invalid legacy exact-line schema")
                        continue
                    values = (variant.get("id"), variant.get("line"))
                    if not all(isinstance(value, str) and value for value in values):
                        errors.append(f"{label}: legacy exact-line values must be non-empty strings")
                        continue
                    if variant["id"] in seen:
                        errors.append(f"{label}: duplicate legacy exact-line id {variant['id']}")
                    seen.add(variant["id"])
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
    *, workspace_hub: str | None = None,
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

    def bind(line: str, task_id: str, source: str, variant_id: str = "") -> None:
        if not isinstance(line, str) or not line:
            raise ValueError(f"{task_id}: exact cron line must be non-empty")
        prior = identities.get(line)
        if prior and prior["catalog_task_id"] != task_id:
            raise ValueError(f"exact cron line collision: {task_id}")
        identities[line] = {"catalog_task_id": task_id, "source": source,
                            "variant_id": variant_id}

    for task in rendered:
        canonical[task["id"]] = [task["line"]]
        bind(task["line"], task["id"], "canonical-exact-line")
    selected_ids = set(canonical)
    groups = (state_classes.get("preserved_external") or []) + (
        state_classes.get("preserved_local") or []
    )
    for row in groups:
        task_id = row.get("catalog_task_id")
        if task_id not in selected_ids:
            continue
        for variant in row.get("legacy_exact_lines") or []:
            legacy.setdefault(task_id, []).append(dict(variant))
            bind(variant["line"], task_id, "legacy-exact-line", variant["id"])
    preservation = [dict(row) for row in groups if row.get("fingerprint")]
    for task in rendered:
        if task.get("installed_fingerprint"):
            preservation.append({"owner": "catalog-preservation-only",
                                 "fingerprint": dict(task["installed_fingerprint"])})
    return {"machine_id": machine_id, "roles": roles, "selected_tasks": rendered,
            "selected_task_ids": selected_ids, "canonical_exact_lines": canonical,
            "legacy_exact_lines": legacy, "line_identities": identities,
            "preservation_fingerprints": preservation}
