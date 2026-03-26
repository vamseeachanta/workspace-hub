"""Tests for the workstation registry and workstation-lib.sh."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "config" / "workstations" / "registry.yaml"
SCHEDULE_TASKS_PATH = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
LIB_SCRIPT = REPO_ROOT / "scripts" / "lib" / "workstation-lib.sh"

REQUIRED_MACHINE_FIELDS = {"hostname", "os", "role", "capabilities", "schedule_variant"}
VALID_SCHEDULE_VARIANTS = {"full", "contribute", "contribute-minimal", "none"}


@pytest.fixture(scope="module")
def registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def machines(registry: dict) -> dict:
    return registry["machines"]


@pytest.fixture(scope="module")
def schedule_tasks() -> list[dict]:
    with open(SCHEDULE_TASKS_PATH) as f:
        data = yaml.safe_load(f)
    return data["tasks"]


# ---------------------------------------------------------------------------
# Registry structure tests
# ---------------------------------------------------------------------------


class TestRegistryStructure:
    def test_registry_loads_valid_yaml(self) -> None:
        """registry.yaml parses without error."""
        with open(REGISTRY_PATH) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert "machines" in data
        assert len(data["machines"]) > 0

    def test_registry_all_machines_have_required_fields(
        self, machines: dict
    ) -> None:
        """Each machine has hostname, os, role, capabilities, schedule_variant."""
        for name, machine in machines.items():
            missing = REQUIRED_MACHINE_FIELDS - set(machine.keys())
            assert not missing, (
                f"Machine '{name}' is missing required fields: {missing}"
            )

    def test_registry_hostnames_unique(self, machines: dict) -> None:
        """No duplicate hostnames across all machines (including aliases)."""
        seen: dict[str, str] = {}  # identifier -> machine key that owns it
        for name, machine in machines.items():
            all_ids = [name, machine["hostname"]] + machine.get(
                "hostname_aliases", []
            )
            for hn in all_ids:
                hn_lower = hn.lower()
                if hn_lower in seen:
                    # Same machine key owning multiple identical ids is fine
                    # (e.g. key == hostname); cross-machine collision is not.
                    assert seen[hn_lower] == name, (
                        f"Duplicate hostname/alias '{hn}' found in both "
                        f"'{seen[hn_lower]}' and '{name}'"
                    )
                else:
                    seen[hn_lower] = name

    def test_registry_ssh_machines_have_workspace_root(
        self, machines: dict
    ) -> None:
        """Machines with ssh != null must have workspace_root."""
        for name, machine in machines.items():
            if machine.get("ssh") is not None:
                ws_root = machine.get("workspace_root")
                assert ws_root is not None and ws_root != "", (
                    f"Machine '{name}' has ssh={machine['ssh']!r} but "
                    f"workspace_root is {ws_root!r}"
                )

    def test_registry_capabilities_not_empty(self, machines: dict) -> None:
        """Every machine has at least one capability."""
        for name, machine in machines.items():
            caps = machine.get("capabilities", {})
            flat: list[str] = []
            for key, val in caps.items():
                if isinstance(val, list):
                    flat.extend(val)
                elif val and val is not False:
                    flat.append(str(val))
            assert flat, (
                f"Machine '{name}' has no capabilities"
            )

    def test_registry_schedule_variants_valid(self, machines: dict) -> None:
        """schedule_variant is one of the allowed values."""
        for name, machine in machines.items():
            variant = machine.get("schedule_variant")
            assert variant in VALID_SCHEDULE_VARIANTS, (
                f"Machine '{name}' has schedule_variant={variant!r}, "
                f"expected one of {VALID_SCHEDULE_VARIANTS}"
            )


# ---------------------------------------------------------------------------
# Cross-reference tests
# ---------------------------------------------------------------------------


class TestRegistryCrossReference:
    @staticmethod
    def _all_registry_identifiers(machines: dict) -> set[str]:
        """Return every machine name, hostname, and alias (lowered)."""
        ids: set[str] = set()
        for name, machine in machines.items():
            ids.add(name.lower())
            ids.add(machine["hostname"].lower())
            for alias in machine.get("hostname_aliases", []):
                ids.add(alias.lower())
        return ids

    def test_registry_matches_schedule_tasks_machines(
        self, machines: dict, schedule_tasks: list[dict]
    ) -> None:
        """Every machine name in schedule-tasks.yaml exists in the registry."""
        valid_ids = self._all_registry_identifiers(machines)
        for task in schedule_tasks:
            for task_machine in task.get("machines", []):
                assert task_machine.lower() in valid_ids, (
                    f"Task '{task['id']}' references machine "
                    f"'{task_machine}' which is not in the registry"
                )

    def test_registry_capabilities_cover_task_requires(
        self, machines: dict, schedule_tasks: list[dict]
    ) -> None:
        """For each task, at least one machine in machines[] has all requires."""
        id_to_machine: dict[str, dict] = {}
        for name, machine in machines.items():
            id_to_machine[name.lower()] = machine
            id_to_machine[machine["hostname"].lower()] = machine
            for alias in machine.get("hostname_aliases", []):
                id_to_machine[alias.lower()] = machine

        for task in schedule_tasks:
            requires = set(task.get("requires", []))
            if not requires:
                continue

            task_machines = task.get("machines", [])
            covered = False
            for tm in task_machines:
                machine = id_to_machine.get(tm.lower())
                if machine is None:
                    continue
                caps = machine.get("capabilities", {})
                # Flatten all capability lists and gpu into a single set
                all_caps: set[str] = set()
                for key, val in caps.items():
                    if isinstance(val, list):
                        all_caps.update(val)
                    elif val and val is not False:
                        all_caps.add(str(val))
                if requires <= all_caps:
                    covered = True
                    break

            assert covered, (
                f"Task '{task['id']}' requires {requires} but none of its "
                f"machines {task_machines} provide all of them"
            )


# ---------------------------------------------------------------------------
# Shell lib tests (subprocess)
# ---------------------------------------------------------------------------


class TestWorkstationLibShell:
    def test_ws_valid_machines_returns_all_names(
        self, machines: dict
    ) -> None:
        """ws_valid_machines returns all machine names, hostnames, and aliases."""
        # Build the expected set from the registry
        expected: set[str] = set()
        for name, machine in machines.items():
            expected.add(name)
            expected.add(machine["hostname"])
            for alias in machine.get("hostname_aliases", []):
                if alias:  # skip empty strings from empty lists
                    expected.add(alias)

        env = os.environ.copy()
        env["WORKSPACE_HUB"] = str(REPO_ROOT)

        # Source the lib and call ws_valid_machines
        result = subprocess.run(
            [
                "bash",
                "-c",
                f'source "{LIB_SCRIPT}" && ws_valid_machines',
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, (
            f"ws_valid_machines failed: stderr={result.stderr}"
        )

        actual = {
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        }

        assert actual == expected, (
            f"ws_valid_machines output mismatch.\n"
            f"  Missing from output: {expected - actual}\n"
            f"  Extra in output:     {actual - expected}"
        )
