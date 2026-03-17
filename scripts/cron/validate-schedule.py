#!/usr/bin/env python3
"""Validate schedule-tasks.yaml — parse, check required fields, cron expressions."""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_FILE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"

REQUIRED_FIELDS = {"id", "label", "schedule", "machines", "command", "description"}
VALID_SCHEDULERS = {"cron", "windows-task-scheduler"}
VALID_MACHINES = {
    "ace-linux-1",
    "ace-linux-2",
    "acma-ansys05",
    "acma-ws014",
    "gali-linux-compute-1",
}


def validate_cron_field(value: str) -> bool:
    """Check that a cron field has valid structure (not full semantic validation)."""
    parts = value.split(",")
    for part in parts:
        part = part.strip()
        if part == "*":
            continue
        if "/" in part:
            base, step = part.split("/", 1)
            if not (base == "*" or base.isdigit()):
                return False
            if not step.isdigit():
                return False
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            if not (lo.isdigit() and hi.isdigit()):
                return False
            continue
        if not part.isdigit():
            return False
    return True


def validate_cron_expression(expr: str) -> list[str]:
    """Return list of errors for a 5-field cron expression."""
    errors = []
    parts = expr.split()
    if len(parts) != 5:
        errors.append(f"Expected 5 fields, got {len(parts)}: '{expr}'")
        return errors
    for i, part in enumerate(parts):
        if not validate_cron_field(part):
            errors.append(f"Invalid cron field {i}: '{part}' in '{expr}'")
    return errors


def main() -> int:
    if not SCHEDULE_FILE.exists():
        print(f"FAIL: {SCHEDULE_FILE} not found")
        return 1

    with open(SCHEDULE_FILE) as f:
        data = yaml.safe_load(f)

    if "tasks" not in data or not isinstance(data["tasks"], list):
        print("FAIL: 'tasks' key missing or not a list")
        return 1

    tasks = data["tasks"]
    errors = []
    ids_seen = set()

    for i, task in enumerate(tasks):
        tid = task.get("id", f"<index-{i}>")

        missing = REQUIRED_FIELDS - set(task.keys())
        if missing:
            errors.append(f"{tid}: missing fields {missing}")

        if tid in ids_seen:
            errors.append(f"{tid}: duplicate ID")
        ids_seen.add(tid)

        scheduler = task.get("scheduler", "cron")
        if scheduler not in VALID_SCHEDULERS:
            errors.append(f"{tid}: invalid scheduler '{scheduler}'")

        for machine in task.get("machines", []):
            if machine not in VALID_MACHINES:
                errors.append(f"{tid}: unknown machine '{machine}'")

        if scheduler == "cron":
            cron_errors = validate_cron_expression(task.get("schedule", ""))
            for ce in cron_errors:
                errors.append(f"{tid}: {ce}")

        if not task.get("command", "").strip():
            errors.append(f"{tid}: empty command")

        # Check if command invokes claude CLI (not just .claude/ paths)
        import re
        cmd = task.get("command", "")
        if re.search(r'(?<!\.)(?<!/)\bclaude\s+--', cmd):
            if not task.get("is_claude_task"):
                errors.append(f"{tid}: invokes claude CLI but is_claude_task != true")

    if errors:
        print(f"FAIL: {len(errors)} error(s) in {SCHEDULE_FILE.name}:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(tasks)} tasks validated in {SCHEDULE_FILE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
