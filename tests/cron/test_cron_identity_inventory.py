"""Task 2 deterministic cron identity inventory tests."""
from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/cron/build-cron-identity-inventory.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("cron_identity_inventory_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_paths(tmp_path: Path, tasks: list[dict], classes: object | None = None):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    state_classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, {"tasks": tasks})
    write_yaml(registry, {"machines": {"linux-a": {
        "hostname": "host-a", "hostname_aliases": ["alias-a"], "os": "linux",
        "harness_profile": {"roles": []},
    }}})
    write_yaml(state_classes, classes if classes is not None else {
        "preserved_external": [], "preserved_local": [],
    })
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(state_classes),
               "--output", str(output)]
    return catalog, state_classes, output, command


def write_yaml(path: Path, value: object) -> None:
    path.write_text(yaml.safe_dump(value), encoding="utf-8")


def test_inventory_is_deterministic_alias_safe_and_check_bound(tmp_path):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, {"tasks": [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo one", "machines": ["linux-a"], "roles": [],
    }]})
    write_yaml(registry, {"machines": {"linux-a": {
        "hostname": "host-a", "hostname_aliases": ["alias-a"], "os": "linux",
        "harness_profile": {"roles": []},
    }}})
    write_yaml(classes, {"preserved_external": [], "preserved_local": []})
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(classes),
               "--output", str(output)]
    assert subprocess.run(command, cwd=ROOT).returncode == 0
    first = output.read_bytes()
    payload = json.loads(first)
    assert payload["machines"] == ["linux-a"]
    assert payload["unsupported"] == []
    assert payload["collisions"] == []
    assert first.endswith(b"\n")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode == 0
    catalog.write_text(catalog.read_text() + "\n", encoding="utf-8")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode != 0


def test_generator_source_is_in_versioned_digest_union(tmp_path):
    generator = load_generator()
    assert SCRIPT in generator.SOURCE_PATHS
    first = tmp_path / "first" / SCRIPT.name
    second = tmp_path / "second" / SCRIPT.name
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(SCRIPT.read_bytes())
    second.write_bytes(SCRIPT.read_bytes() + b"\n# source drift\n")
    assert generator.input_digest([first]) != generator.input_digest([second])


def test_duplicate_exact_lines_emit_collision_and_non_unique_rows(tmp_path):
    tasks = [
        {"id": task_id, "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo same", "machines": ["linux-a"], "roles": []}
        for task_id in ("one", "two")
    ]
    _catalog, _classes, output, command = fixture_paths(tmp_path, tasks)
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    payload = json.loads(output.read_bytes())
    assert payload["collisions"]
    assert {row["unique"] for row in payload["identities"]} == {False}


def test_unsupported_render_is_named_and_fails(tmp_path):
    task = {"id": "bad", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo bad", "machines": ["linux-a"],
            "roles": [{"unsupported": "mapping"}]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task])
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    assert json.loads(output.read_bytes())["unsupported"]


def test_unbound_legacy_variant_is_named_and_fails(tmp_path):
    task = {"id": "other", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo other", "machines": ["elsewhere"], "roles": []}
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "linux-a", "catalog_task_id": "other",
        "legacy_exact_lines": [{"id": "old", "line": "0 1 * * * echo old"}],
    }]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    assert subprocess.run(command, cwd=ROOT).returncode != 0
    unsupported = json.loads(output.read_bytes())["unsupported"]
    assert unsupported == [{"error": "legacy variant is not bound in a canonical Linux context",
                            "task_id": "other", "variant_id": "old"}]


@pytest.mark.parametrize("malformed", [None, 7, ["not", "a", "mapping"]])
def test_malformed_state_classes_fail_without_traceback(tmp_path, malformed):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    _catalog, state_classes, output, command = fixture_paths(tmp_path, [task])
    state_classes.write_text(yaml.safe_dump(malformed), encoding="utf-8")
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert not output.exists()
    assert "state classes root must be a mapping" in completed.stderr
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize(
    ("catalog_data", "registry_data", "message"),
    [
        (None, {"machines": {"linux-a": {"os": "linux"}}}, "catalog root"),
        ({}, {"machines": {"linux-a": {"os": "linux"}}}, "non-empty tasks"),
        ({"tasks": []}, {"machines": {"linux-a": {"os": "linux"}}}, "non-empty tasks"),
        ({"tasks": [{"id": "one"}]}, None, "registry root"),
        ({"tasks": [{"id": "one"}]}, {}, "canonical Linux machine"),
        ({"tasks": [{"id": "one"}]}, {"machines": {}}, "canonical Linux machine"),
        ({"tasks": [{"id": "one"}]}, {"machines": {"win": {"os": "windows"}}},
         "canonical Linux machine"),
    ],
)
def test_inventory_rejects_empty_or_missing_required_roots(
    tmp_path, catalog_data, registry_data, message
):
    catalog = tmp_path / "catalog.yaml"
    registry = tmp_path / "registry.yaml"
    classes = tmp_path / "classes.yaml"
    output = tmp_path / "inventory.json"
    write_yaml(catalog, catalog_data)
    write_yaml(registry, registry_data)
    write_yaml(classes, {"preserved_external": [], "preserved_local": []})
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(classes),
               "--output", str(output)]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert message in completed.stderr
    assert not output.exists()


def test_inventory_rejects_duplicate_task_ids_in_write_and_check_modes(tmp_path):
    task = {"id": "duplicate", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    catalog, _classes, output, command = fixture_paths(tmp_path, [task, dict(task)])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "duplicate task id" in completed.stderr
    assert not output.exists()
    output.write_text("{}\n", encoding="utf-8")
    checked = subprocess.run(command + ["--check"], cwd=ROOT, text=True, capture_output=True)
    assert checked.returncode != 0
    assert "duplicate task id" in checked.stderr


def test_inventory_rejects_legacy_lines_without_task_binding(tmp_path):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "local",
        "legacy_exact_lines": [{"id": "old", "line": "0 1 * * * echo old"}],
    }]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "legacy_exact_lines requires catalog_task_id" in completed.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    "fingerprint",
    [
        {"command_tokens": "python x.py"},
        {"command_tokens": ["python", True]},
        {"cwd_contains": ["/repo"]},
        {"cwd_basename": False},
        {"script_basename": ["x.py"]},
        {"command_contains": 7},
        {"command_contains": []},
    ],
)
def test_inventory_rejects_runtime_incompatible_fingerprint_types(
    tmp_path, fingerprint
):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    classes = {"preserved_external": [{
        "owner": "external", "fingerprint": fingerprint,
    }], "preserved_local": []}
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task], classes)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode != 0
    assert "fingerprint" in completed.stderr
    assert not output.exists()
