#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Pure, testable core for the workspace-hub fail-closed crontab transaction.

This module contains NO file IO (except an optional __main__ self-check). All
functions take dict/str in and return dict/str/tuple out, so they are trivially
unit-testable and safe to wire into setup-cron.sh and cron-audit.py.

See issue #2969 — "F2: role-tagged cron catalog + safe cutover".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from cron_render import render_cron_line  # noqa: E402
from cron_identity import build_ownership_context  # noqa: E402,F401
from cron_line_model import (  # noqa: E402,F401
    MARKER_BEGIN_RE,
    MARKER_END,
    classify_line,
    classify_line_detail,
    marker_begin,
    match_fingerprint,
    normalize_preserved_entries,
    parse_crontab,
)

_SCRIPT_PATH_RE = re.compile(r"scripts/[\w./-]+\.(?:sh|py)")

# --- Task selection --------------------------------------------------------


def select_tasks(
    tasks: list[dict],
    machine_roles: list[str],
    machine_id: str | set[str] | list[str] | tuple[str, ...],
) -> tuple[list[dict], list[dict]]:
    """Select catalog tasks for this machine by role and/or legacy machine pin.

    A task is selected if its `roles` intersect `machine_roles`, OR `machine_id`
    is in its legacy `machines` list. Deduped by task['id'].

    Conflict: role-match selects it, but a non-empty legacy `machines` list
    EXCLUDES this machine_id. Resolution: roles win iff
    `task.get('roles_authoritative')` is True; otherwise legacy wins (not
    selected). Conflicts are reported for auditing regardless of outcome.

    Returns (selected_tasks_sorted_by_id, conflicts) where each conflict is
    {"id": ..., "reason": ...}.
    """
    role_set = set(machine_roles or [])
    raw_tokens = {machine_id} if isinstance(machine_id, str) else set(machine_id or set())
    machine_tokens = {str(token).lower() for token in raw_tokens if str(token).strip()}
    selected_by_id: dict = {}
    conflicts: list[dict] = []
    for task in tasks or []:
        if task.get("scheduler", "cron") != "cron":
            continue
        selected, conflict = _task_selection(task, role_set, machine_tokens)
        if conflict:
            conflicts.append(conflict)
        if selected:
            selected_by_id[task.get("id")] = task
    return sorted(selected_by_id.values(), key=lambda task: task.get("id")), conflicts


def _task_selection(task, role_set, machine_tokens):
    task_id = task.get("id")
    role_match = bool(set(task.get("roles", []) or []) & role_set)
    machines = task.get("machines")
    has_machines = isinstance(machines, list) and bool(machines)
    pins = {str(machine).lower() for machine in machines or []}
    machine_match = bool(pins & machine_tokens)
    if not (role_match and has_machines and not machine_match):
        return role_match or machine_match, None
    authoritative = bool(task.get("roles_authoritative"))
    outcome = (
        "roles_authoritative=True → roles win (selected)" if authoritative
        else "roles_authoritative not set → legacy wins (not selected)"
    )
    return authoritative, {
        "id": task_id,
        "reason": f"role-match vs legacy machines exclusion; {outcome}",
    }


def _normalize_command(command: str) -> str:
    return " ".join(str(command).split())


def catalog_command_keys(
    tasks: list[dict],
    fallback_mode: str = "full-command",
    include_fingerprinted: bool = True,
) -> list[str]:
    """Return stable catalog keys for matching live cron lines.

    Prefer a repository-relative script token. When no script token exists, use
    the full normalized command. Do not truncate fallback keys: truncated keys
    collide and misclassify unrelated live lines.
    """
    keys: list[str] = []
    seen: set[str] = set()
    for task in tasks or []:
        if task.get("installed_fingerprint") and not include_fingerprinted:
            continue
        command = _normalize_command(task.get("command", ""))
        if not command:
            continue
        match = _SCRIPT_PATH_RE.search(command)
        key = match.group(0) if match else command if fallback_mode == "full-command" else ""
        if key and key not in seen:
            keys.append(key)
            seen.add(key)
    return keys


def catalog_owned_fingerprints(tasks: list[dict]) -> list[dict]:
    """Return explicit all-fields-match ownership records for catalog tasks."""
    records = []
    for task in tasks or []:
        fingerprint = task.get("installed_fingerprint")
        if fingerprint:
            records.append({
                "catalog_task_id": task.get("id"),
                "fingerprint": dict(fingerprint),
            })
    return normalize_preserved_entries(records)


# --- Rendering -------------------------------------------------------------


def render_block(tasks: list[dict], roles: list[str]) -> list[str]:
    """Render the managed block (begin marker + task lines + end marker).

    Task lines are "{schedule} {command}", sorted by id for determinism.
    Idempotent: same input → same output.
    """
    sorted_tasks = sorted(tasks or [], key=lambda t: t.get("id"))
    lines = [marker_begin(roles)]
    for task in sorted_tasks:
        lines.append(render_cron_line(task["schedule"], task["command"]))
    lines.append(MARKER_END)
    return lines


# --- Cutover planning ------------------------------------------------------


def plan_cutover(
    current_text: str,
    selected_tasks: list[dict],
    roles: list[str],
    catalog_commands: list[str],
    external_fingerprints: list[dict],
    selected_task_ids: set[str] | None = None,
    catalog_fingerprints: list[dict] | None = None,
    ownership_context: dict | None = None,
) -> dict:
    """Plan a fail-closed, idempotent replacement of the managed cron block."""
    parsed = parse_crontab(current_text)
    if parsed["error"]:
        return {
            "new_text": None,
            "preserved": [],
            "uncataloged": [],
            "conflicts": [],
            "abort_reason": parsed["error"],
        }

    classify = _line_classifier(
        catalog_commands, external_fingerprints, selected_task_ids,
        catalog_fingerprints, ownership_context,
    )
    preserved, uncataloged = _classify_nonmanaged(parsed, classify)
    if uncataloged:
        return {
            "new_text": None,
            "preserved": preserved,
            "uncataloged": uncataloged,
            "conflicts": [],
            "abort_reason": f"uncataloged live cron line(s): {uncataloged}",
        }

    new_lines = _rebuild_lines(parsed, render_block(selected_tasks, roles), classify)
    new_text = "\n".join(new_lines)
    if parsed.get("_trailing_newline"):
        new_text += "\n"

    return {
        "new_text": new_text,
        "preserved": preserved,
        "uncataloged": [],
        "conflicts": [],
            "abort_reason": None,
    }


def _classify_nonmanaged(parsed, classify):
    preserved, uncataloged = [], []
    for line in list(parsed["before"]) + list(parsed["after"]):
        line_class = classify(line)
        if line_class in ("ignore", "preserved_external"):
            preserved.append(line)
        elif line_class != "cataloged":
            uncataloged.append(line)
    return preserved, uncataloged


def _line_classifier(commands, fingerprints, selected_ids, catalog_fps, ownership):
    def classify(line):
        return classify_line_detail(
            line, commands, fingerprints, selected_task_ids=selected_ids,
            catalog_fingerprints=catalog_fps, ownership_context=ownership,
        )["class"]
    return classify


def _rebuild_lines(parsed, block, classify):
    before = [line for line in parsed["before"] if classify(line) != "cataloged"]
    if parsed["roles"] is None:
        return before + block
    after = [line for line in parsed["after"] if classify(line) != "cataloged"]
    return before + block + after


if __name__ == "__main__":
    # Optional thin self-check (no external IO).
    sample = "MAILTO=ops@example.com\n0 * * * * echo hi\n"
    tasks = [{"id": "b", "schedule": "0 1 * * *", "command": "run-b"},
             {"id": "a", "schedule": "0 2 * * *", "command": "run-a"}]
    sel, conflicts = select_tasks(tasks, ["worker"], "host1")
    plan = plan_cutover(
        sample,
        tasks,
        ["worker"],
        catalog_commands=["echo hi"],
        external_fingerprints=[],
    )
    print("self-check abort_reason:", plan["abort_reason"])
    print(plan["new_text"])
    # Idempotency probe.
    plan2 = plan_cutover(
        plan["new_text"], tasks, ["worker"],
        catalog_commands=["echo hi"], external_fingerprints=[],
    )
    print("idempotent:", plan["new_text"] == plan2["new_text"])
