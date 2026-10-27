#!/usr/bin/env python3
"""Render declared task cadences as Markdown without running task commands.

Usage: build-cadence-schedule.sh --input catalog.yaml --output index.md
       --registry registry.yaml

Targets are canonicalized and deduplicated through cron_render; schedule
precedence is shared with the installer. Missing cadence metadata is displayed
as unspecified rather than inferred. Cron validation is structural only, as in
validate-schedule.py; time ranges and scheduler-specific triggers are not checked.
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
import sys
from typing import Any

import yaml

from cron_render import build_context, effective_schedule


ROOT = Path(__file__).resolve().parents[2]  # scripts/cron is two levels below root.
DEFAULT_INPUT = ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
DEFAULT_REGISTRY = ROOT / "config" / "workstations" / "registry.yaml"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "cadence-schedule.md"


class _UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        if len(mapping) != len(node.value):
            raise yaml.constructor.ConstructorError(
                None, None, "duplicate mapping key", node.start_mark
            )
        return mapping


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _schedule(value: Any, scheduler: str) -> str:
    value = _text(value, "schedule")
    # Five fields follow validate-schedule.py:validate_cron_expression.
    # Macro declarations remain literal, as in cron_render.effective_schedule.
    if scheduler != "cron" or value in {
        "@reboot", "@yearly", "@annually", "@monthly", "@weekly",
        "@daily", "@midnight", "@hourly",
    }:
        return value
    field = r"(?:\*|\d+(?:-\d+)?)(?:/\d+)?"
    if len(value.split()) != 5 or any(
        not re.fullmatch(rf"{field}(?:,{field})*", part) for part in value.split()
    ):
        raise ValueError("schedule must have five cron fields or a cron macro")
    return value


def _load(path: Path, label: str) -> dict[str, Any]:
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read {label}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid {label} YAML") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a mapping")
    return data


def _validate_registry(registry: dict[str, Any]) -> None:
    machines = registry.get("machines", {})
    if not isinstance(machines, dict):
        raise ValueError("registry machines must be a mapping")
    for key, entry in machines.items():
        _text(key, "registry target")
        if not isinstance(entry, dict):
            raise ValueError("registry target must be a mapping")
        if "hostname" in entry:
            _text(entry["hostname"], "registry hostname")
        aliases = entry.get("hostname_aliases", [])
        if not isinstance(aliases, list):
            raise ValueError("registry hostname_aliases must be a list")
        for alias in aliases:
            _text(alias, "registry alias")


def _validate_tasks(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = catalog.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("each task must be a mapping")
        task_id = _text(task.get("id"), "id")
        if task_id in seen:
            raise ValueError("duplicate task id")
        seen.add(task_id)
        scheduler = task.get("scheduler", "cron")
        # Scheduler choices and default follow validate-schedule.py and cron_render.
        if scheduler not in ("cron", "windows-task-scheduler"):
            raise ValueError("scheduler must be cron or windows-task-scheduler")
        _schedule(task.get("schedule"), scheduler)
        if "cadence" in task:
            _text(task["cadence"], "cadence")
        machines = task.get("machines", [])
        if not isinstance(machines, list):
            raise ValueError("machines must be a list")
        for machine in machines:
            _text(machine, "machines entry")
        overrides = task.get("schedule_by_machine", {})
        if not isinstance(overrides, dict):
            raise ValueError("schedule_by_machine must be a mapping")
        tokens: set[str] = set()
        for token, schedule in overrides.items():
            normalized = _text(token, "schedule_by_machine key").lower()
            if normalized in tokens:
                raise ValueError("duplicate schedule_by_machine key after normalization")
            tokens.add(normalized)
            _schedule(schedule, scheduler)
    return tasks


def _cell(value: str) -> str:
    """Keep data within a single Markdown table cell, including HTML-like text."""
    return (html.escape(value, quote=False).replace("|", "&#124;")
            .replace("\\", "&#92;").replace("`", "&#96;")
            .replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>"))


def render_index(catalog: dict[str, Any], registry: dict[str, Any]) -> str:
    """Validate all declarations before producing deterministic index text."""
    tasks = _validate_tasks(catalog)
    _validate_registry(registry)
    lines = [
        "# Cadence schedule", "",
        "Declared schedules only; this index does not install or execute tasks.",
        "Cadence is unspecified where the catalog does not declare it.", "",
        "| Task | Cadence | Scheduler | Target | Schedule |",
        "| --- | --- | --- | --- | --- |",
    ]
    for task in sorted(tasks, key=lambda item: item["id"].strip()):
        # Resolve aliases explicitly: never use the executing computer as a target.
        targets: dict[str, str] = {}
        for declared in task.get("machines", []):
            context = build_context(declared, registry=registry)
            target = context["machine_id"]
            schedule = effective_schedule(task, context)
            if target in targets and targets[target] != schedule:
                raise ValueError("conflicting schedules for aliases of the same target")
            targets[target] = schedule
        if not targets:
            targets["unspecified"] = effective_schedule(task, {})
        for target, schedule in sorted(targets.items()):
            cells = [
                task["id"].strip(), task.get("cadence", "unspecified").strip(),
                task.get("scheduler", "cron"), target, schedule,
            ]
            lines.append("| " + " | ".join(_cell(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() in {args.input.resolve(), args.registry.resolve()}:
            raise ValueError("output must differ from input and registry")
        result = render_index(_load(args.input, "input"), _load(args.registry, "registry"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    except (ValueError, OSError, UnicodeError) as exc:
        # Validation errors are contextual but do not echo catalog values or paths.
        # Unexpected programming errors retain their traceback for diagnosis.
        message = str(exc) if isinstance(exc, ValueError) else "cannot write output"
        print(f"cadence-schedule: {message}", file=sys.stderr)
        return 1  # CLI failure convention.
    return 0  # CLI success convention.


if __name__ == "__main__":
    raise SystemExit(main())
