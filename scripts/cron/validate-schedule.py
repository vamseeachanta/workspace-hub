#!/usr/bin/env python3
"""Validate schedule-tasks.yaml — parse, check required fields, cron expressions."""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_FILE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
REGISTRY_FILE = REPO_ROOT / "config" / "workstations" / "registry.yaml"
ROLES_FILE = REPO_ROOT / "config" / "workstations" / "harness-roles.yaml"

REQUIRED_FIELDS = {"id", "label", "schedule", "machines", "command", "description"}
VALID_SCHEDULERS = {"cron", "windows-task-scheduler"}
MIN_RUNTIME_SECONDS = 60
MAX_RUNTIME_SECONDS = 604_800


def _load_valid_machines() -> set[str]:
    """Build valid machine names from the workstation registry."""
    if not REGISTRY_FILE.exists():
        # Fallback if registry is missing
        return {
            "dev-primary", "ace-linux-1", "dev-secondary", "ace-linux-2",
            "ace-win-1", "ace-win-2", "licensed-win-1", "licensed-win-2",
            "gali-linux-compute-1",
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


def _load_valid_roles() -> set[str]:
    """Build valid role names from the harness-roles catalog (excluding _base)."""
    if not ROLES_FILE.exists():
        return set()
    with open(ROLES_FILE) as f:
        data = yaml.safe_load(f)
    roles: set[str] = set(data.get("roles", {}).keys())
    roles.discard("_base")  # _base is the implicit floor, not a selectable task role
    return roles


VALID_ROLES = _load_valid_roles()


def validate_runtime_contract(tid: str, runtime: object, state_dirs: set[str]) -> list[str]:
    """Validate the optional bounded runtime-health contract."""
    if runtime is None:
        return []
    if not isinstance(runtime, dict):
        return [f"{tid}: runtime must be a mapping"]
    errors: list[str] = []
    singleton = runtime.get("singleton")
    maximum = runtime.get("max_seconds")
    state_dir = runtime.get("state_dir")
    if not isinstance(singleton, bool):
        errors.append(f"{tid}: runtime.singleton must be boolean")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or not MIN_RUNTIME_SECONDS <= maximum <= MAX_RUNTIME_SECONDS:
        errors.append(f"{tid}: runtime.max_seconds must be an integer from 60 to 604800")
    path = Path(state_dir) if isinstance(state_dir, str) else None
    if not path or path.is_absolute() or ".." in path.parts or not path.parts:
        errors.append(f"{tid}: runtime.state_dir must be controlled and repo-relative")
    elif state_dir in state_dirs:
        errors.append(f"{tid}: duplicate runtime.state_dir '{state_dir}'")
    else:
        state_dirs.add(state_dir)
    channels = runtime.get("filesystem_wait_wchans", [])
    if not isinstance(channels, list) or any(not isinstance(item, str) or not item.replace("_", "").isalnum() for item in channels):
        errors.append(f"{tid}: runtime.filesystem_wait_wchans contains an invalid token")
    return errors


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
    state_dirs: set[str] = set()

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

        for role in task.get("roles", []):
            if VALID_ROLES and role not in VALID_ROLES:
                errors.append(f"{tid}: unknown role '{role}' in roles")

        if scheduler == "cron":
            cron_errors = validate_cron_expression(task.get("schedule", ""))
            for ce in cron_errors:
                errors.append(f"{tid}: {ce}")

        if not task.get("command", "").strip():
            errors.append(f"{tid}: empty command")

        if scheduler != "cron" and task.get("runtime") is not None:
            errors.append(f"{tid}: runtime metadata is supported only for cron tasks")
        errors.extend(validate_runtime_contract(tid, task.get("runtime"), state_dirs))

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
