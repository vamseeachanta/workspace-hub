#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Shared cron task renderer.

This module is intentionally leaf-level: it knows how to resolve a machine,
choose the effective cron schedule, and expand render-time placeholders. It does
not know anything about crontab cutover transactions.
"""
from __future__ import annotations

import argparse
import os
import re
import socket
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
DEFAULT_SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
FULL_VARIANT_LOG = "logs/quality/cron-wrapper.log"
CONTRIBUTE_LOG = "/tmp/workspace-hub-cron.log"
_PLACEHOLDER_RE = re.compile(
    r"\$(?:{(?P<braced>WORKSPACE_HUB|LOG)}|(?P<bare>WORKSPACE_HUB|LOG)(?![A-Za-z0-9_]))"
)


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def _norm(value: object) -> str:
    return str(value).strip().lower()


def _host_token(value: str | None = None) -> str:
    raw = value or socket.gethostname().split(".")[0]
    return _norm(raw.split(".")[0])


def machine_tokens(machine_id: str, machine: dict[str, Any]) -> set[str]:
    tokens = {machine_id}
    hostname = machine.get("hostname")
    if hostname:
        tokens.add(str(hostname))
    tokens.update(str(alias) for alias in machine.get("hostname_aliases", []) or [])
    return {_norm(token) for token in tokens if str(token).strip()}


def resolve_machine(
    machine: str | None = None,
    *,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve a hostname, alias, or canonical machine id through registry.yaml."""
    registry = registry if registry is not None else _load_yaml(DEFAULT_REGISTRY)
    requested = _host_token(machine)
    machines = registry.get("machines", {}) or {}
    for machine_id, entry in machines.items():
        tokens = machine_tokens(machine_id, entry or {})
        if requested in tokens:
            return {
                "machine_id": machine_id,
                "machine": entry or {},
                "input_token": requested,
                "tokens": tokens,
                "known": True,
            }
    return {
        "machine_id": requested,
        "machine": {},
        "input_token": requested,
        "tokens": {requested} if requested else set(),
        "known": False,
    }


def workspace_hub_path(workspace_hub: str | Path | None = None) -> str:
    """Return the declared target path without applying host path semantics."""
    override = workspace_hub or os.environ.get("WORKSPACE_HUB")
    return str(override) if override else str(REPO_ROOT)


def build_context(
    machine: str | None = None,
    *,
    registry: dict[str, Any] | None = None,
    workspace_hub: str | Path | None = None,
) -> dict[str, Any]:
    resolved = resolve_machine(machine, registry=registry)
    entry = resolved["machine"]
    hub = workspace_hub_path(workspace_hub)
    schedule_variant = entry.get("schedule_variant", "contribute")
    hub_prefix = hub.rstrip("/\\")
    log = f"{hub_prefix}/{FULL_VARIANT_LOG}" if schedule_variant == "full" else CONTRIBUTE_LOG

    hostname = _norm(entry.get("hostname") or resolved["input_token"])
    aliases = [_norm(alias) for alias in entry.get("hostname_aliases", []) or []]
    ordered_schedule_tokens: list[str] = []
    for token in [hostname, resolved["machine_id"], resolved["input_token"], *aliases, *sorted(resolved["tokens"])]:
        token = _norm(token)
        if token and token not in ordered_schedule_tokens:
            ordered_schedule_tokens.append(token)

    return {
        **resolved,
        "workspace_hub": hub,
        "log": log,
        "schedule_variant": schedule_variant,
        "schedule_tokens": ordered_schedule_tokens,
        # Scheduler routing (#3507): setup-cron.sh must key its Windows-Task-Scheduler
        # skip on the registry os, not the schedule variant. Default linux — a missing
        # os must not silently skip cron reconciliation.
        "os": str(entry.get("os") or "linux").lower(),
    }


def effective_schedule(task: dict[str, Any], context: dict[str, Any]) -> str:
    schedule_by_machine = task.get("schedule_by_machine") or {}
    if isinstance(schedule_by_machine, dict):
        lowered = {_norm(key): value for key, value in schedule_by_machine.items()}
        for token in context.get("schedule_tokens", []) or []:
            if token in lowered:
                return str(lowered[token]).strip()
    return str(task.get("schedule", "")).strip()


def expand_command(command: str, context: dict[str, Any]) -> str:
    values = {
        "WORKSPACE_HUB": context["workspace_hub"],
        "LOG": context["log"],
    }

    def replace(match: re.Match[str]) -> str:
        key = match.group("braced") or match.group("bare")
        return values[key]

    return _PLACEHOLDER_RE.sub(replace, str(command).strip())


def render_cron_line(schedule: str, command: str) -> str:
    return f"{str(schedule).strip()} {str(command).strip()}"


def _ensure_log_dir(command: str, log: Any) -> str:
    """Prepend `mkdir -p $WORKSPACE_HUB/<logdir>` so a cron `>>` redirect never
    fails on a missing parent directory — cron cannot create it, and a failed
    redirect makes the job produce no log (reads as MISSING in cron-health even
    though the job is fine). The dir is derived from the task's catalog `log:`
    field. No-op for absolute/non-standard logs, or when the command already
    ensures the dir (e.g. the email tasks that mkdir -p inline)."""
    if not command or not log:
        return command
    log = str(log).strip()
    if not log.startswith("logs/"):
        return command
    log_dir = log.rsplit("/", 1)[0]
    if "mkdir -p" in command and log_dir in command:
        return command
    return f"mkdir -p $WORKSPACE_HUB/{log_dir} && {command}"


def render_task(task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    schedule = effective_schedule(task, context)
    command = _ensure_log_dir(task.get("command", ""), task.get("log"))
    command = expand_command(command, context)
    rendered = dict(task)
    rendered["schedule"] = schedule
    rendered["command"] = command
    rendered["line"] = render_cron_line(schedule, command)
    rendered["machine_id"] = context["machine_id"]
    return rendered


def select_machine_tasks(
    tasks: list[dict[str, Any]],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Machine-token-only selection for the legacy setup-cron installer."""
    tokens = set(context.get("tokens", set()) or set())
    selected: list[dict[str, Any]] = []
    for task in tasks or []:
        if task.get("scheduler", "cron") != "cron":
            continue
        task_machines = {_norm(machine) for machine in task.get("machines", []) or []}
        if tokens & task_machines:
            selected.append(task)
    return selected


def render_machine_cron_lines(
    tasks: list[dict[str, Any]],
    context: dict[str, Any],
) -> list[str]:
    lines: list[str] = []
    for task in select_machine_tasks(tasks, context):
        rendered = render_task(task, context)
        if rendered["schedule"] and rendered["command"]:
            lines.append(rendered["line"])
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hostname", "--machine", dest="machine", default=None)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--schedule-file", type=Path, default=None)
    parser.add_argument("--cron-lines", action="store_true")
    parser.add_argument(
        "--field",
        choices=["machine_id", "schedule_variant", "workspace_hub", "log", "known", "os"],
        default=None,
    )
    args = parser.parse_args(argv)

    registry = _load_yaml(args.registry)
    context = build_context(args.machine, registry=registry)
    if args.field:
        value = context[args.field]
        if isinstance(value, bool):
            value = "true" if value else "false"
        print(value)
        return 0

    if args.cron_lines or args.schedule_file:
        schedule_path = args.schedule_file or DEFAULT_SCHEDULE
        data = _load_yaml(schedule_path)
        for line in render_machine_cron_lines(data.get("tasks", []) or [], context):
            print(line)
        return 0

    print(context["machine_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
