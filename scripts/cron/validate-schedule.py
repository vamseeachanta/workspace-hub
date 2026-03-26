#!/usr/bin/env python3
"""Validate schedule-tasks.yaml — parse, check required fields, cron expressions."""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_FILE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
REGISTRY_FILE = REPO_ROOT / "config" / "workstations" / "registry.yaml"

REQUIRED_FIELDS = {"id", "label", "schedule", "machines", "command", "description"}
VALID_SCHEDULERS = {"cron", "windows-task-scheduler"}


def _load_valid_machines() -> set[str]:
    """Build valid machine names from the workstation registry."""
    if not REGISTRY_FILE.exists():
        # Fallback if registry is missing
        return {
            "dev-primary", "ace-linux-1", "dev-secondary", "ace-linux-2",
            "licensed-win-1", "licensed-win-2", "gali-linux-compute-1",
        }
    with open(REGISTRY_FILE) as f:
        data = yaml.safe_load(f)
    machines: set[str] = set()
    for name, m in data.get("machines", {}).items():
        machines.add(name)
        machines.add(m["hostname"])
        for alias in m.get("hostname_aliases", []):
            machines.add(alias)
    return machines


VALID_MACHINES = _load_valid_machines()


def _load_valid_capabilities() -> set[str]:
    """Build valid capability names from the workstation registry."""
    if not REGISTRY_FILE.exists():
        return set()
    with open(REGISTRY_FILE) as f:
        data = yaml.safe_load(f)
    caps: set[str] = set()
    for _name, m in data.get("machines", {}).items():
        c = m.get("capabilities", {})
        for key in ("agent_clis", "languages", "tools"):
            caps.update(c.get(key, []))
        gpu = c.get("gpu")
        if gpu and gpu is not True:
            caps.add(gpu)
        if gpu:
            caps.add("gpu")
    return caps


VALID_CAPABILITIES = _load_valid_capabilities()


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

        for cap in task.get("requires", []):
            if VALID_CAPABILITIES and cap not in VALID_CAPABILITIES:
                errors.append(f"{tid}: unknown capability '{cap}' in requires")

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
