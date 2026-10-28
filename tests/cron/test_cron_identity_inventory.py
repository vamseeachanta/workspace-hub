"""Task 2 deterministic cron identity inventory tests."""
from __future__ import annotations

import hashlib
import json
import importlib.util
import re
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
        "workspace_root": "/canonical/workspace-hub",
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
        "workspace_root": "/canonical/workspace-hub",
        "harness_profile": {"roles": []},
    }}})
    write_yaml(classes, {"preserved_external": [], "preserved_local": []})
    command = [sys.executable, str(SCRIPT), "--catalog", str(catalog),
               "--registry", str(registry), "--state-classes", str(classes),
               "--output", str(output)]
    assert subprocess.run(command, cwd=ROOT).returncode == 0
    first = output.read_bytes()
    payload = json.loads(first)
    assert payload["machines"] == [hashlib.sha256(b"cron-machine:linux-a").hexdigest()[:12]]
    assert payload["unsupported"] == []
    assert payload["collisions"] == []
    assert first.endswith(b"\n")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode == 0
    catalog.write_text(catalog.read_text() + "\n", encoding="utf-8")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode != 0


def test_public_machine_keys_are_opaque_stable_and_distinct(tmp_path):
    generator = load_generator()
    catalog, classes, output, command = fixture_paths(tmp_path, [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo one", "machines": ["linux-a", "linux-b"], "roles": [],
    }])
    registry = tmp_path / "registry.yaml"
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["machines"]["linux-b"] = {
        "os": "linux", "workspace_root": str(tmp_path / "declared"),
        "harness_profile": {"roles": []},
    }
    write_yaml(registry, data)

    assert subprocess.run(command, cwd=ROOT).returncode == 0
    first = output.read_bytes()
    assert subprocess.run(command, cwd=ROOT).returncode == 0
    assert output.read_bytes() == first
    assert all(key.encode() not in first for key in data["machines"])
    payload = json.loads(first)
    expected = [hashlib.sha256(f"cron-machine:{key}".encode()).hexdigest()[:12]
                for key in sorted(data["machines"])]
    assert payload["machines"] == expected
    assert len(set(expected)) == 2
    assert all(re.fullmatch(r"[0-9a-f]{12}", key) for key in expected)
    assert [row["machine_id"] for row in payload["identities"]] == expected

    # Registry insertion order must not affect the published keys or row order.
    data["machines"] = dict(reversed(list(data["machines"].items())))
    write_yaml(registry, data)
    reordered = generator.build(catalog, registry, classes)
    assert reordered["machines"] == expected
    assert reordered["identities"] == payload["identities"]


def test_public_projection_preserves_ownership_legacy_and_collisions(tmp_path):
    tasks = [{
        "id": task_id, "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo same", "machines": ["alias-a"], "roles": [],
    } for task_id in ("one", "two")]
    tasks.append({
        "id": "excluded", "scheduler": "cron", "schedule": "0 2 * * *",
        "command": "echo excluded", "machines": ["elsewhere"], "roles": [],
    })
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "local", "catalog_task_id": "one",
        "legacy_exact_lines": [{"id": "old", "line": "0 2 * * * echo old"}],
    }]}
    _catalog, _classes, output, command = fixture_paths(tmp_path, tasks, classes)
    assert subprocess.run(command, cwd=ROOT).returncode == 1
    payload = json.loads(output.read_bytes())
    key = hashlib.sha256(b"cron-machine:linux-a").hexdigest()[:12]
    line_hash = hashlib.sha256(b"0 1 * * * echo same").hexdigest()
    # These rows are the pre-projection generator's results for this fixture,
    # with only the canonical machine key replaced at the public boundary.
    assert payload["machines"] == [key]
    assert payload["identities"] == [{
        "canonical_line_sha256": line_hash,
        "legacy_variant_ids": variants, "machine_id": key,
        "task_id": task_id, "unique": False,
    } for task_id, variants in (("one", ["old"]), ("two", []))]
    assert payload["collisions"] == [{
        "machine_id": key, "task_ids": ["one", "two"], "line_sha256": line_hash,
    }]
    assert payload["unsupported"] == []
    assert b"linux-a" not in output.read_bytes()


@pytest.mark.parametrize("failure", ["missing-root", "invalid-role"])
def test_public_machine_keys_cover_unsupported_rows(tmp_path, failure):
    task = {
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo one", "machines": ["linux-a"], "roles": [],
    }
    if failure == "invalid-role":
        task["roles"] = [{"unsupported": "mapping"}]
    _catalog, _classes, output, command = fixture_paths(tmp_path, [task])
    registry = tmp_path / "registry.yaml"
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    if failure == "missing-root":
        del data["machines"]["linux-a"]["workspace_root"]
        write_yaml(registry, data)
    assert subprocess.run(command, cwd=ROOT).returncode == 1
    payload = json.loads(output.read_bytes())
    assert payload["identities"] == []
    assert payload["collisions"] == []
    assert len(payload["unsupported"]) == 1
    assert payload["unsupported"][0]["machine_id"] == payload["machines"][0]
    assert all(key.encode() not in output.read_bytes() for key in data["machines"])


def test_public_machine_key_collision_fails_closed(tmp_path, monkeypatch):
    generator = load_generator()
    catalog, classes, _output, _command = fixture_paths(tmp_path, [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "echo one", "machines": [], "roles": [],
    }])
    registry = tmp_path / "registry.yaml"
    write_yaml(registry, {"machines": {
        key: {"os": "linux"} for key in ("linux-a", "linux-b")
    }})
    monkeypatch.setattr(generator, "public_machine_key", lambda key: "0" * 12)
    with pytest.raises(ValueError, match="public machine key collision"):
        generator.build(catalog, registry, classes)


def test_inventory_uses_registry_workspace_not_checkout_environment(tmp_path, monkeypatch):
    generator = load_generator()
    catalog, classes, _output, _command = fixture_paths(tmp_path, [{
        "id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
        "command": "$WORKSPACE_HUB/scripts/run.sh", "machines": ["linux-a"],
        "roles": [],
    }])
    registry = tmp_path / "registry.yaml"
    registry_data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    registry_data["machines"]["linux-a"]["workspace_root"] = "/canonical/workspace-hub"
    write_yaml(registry, registry_data)

    monkeypatch.setenv("WORKSPACE_HUB", "/checkout/one")
    first = generator.build(catalog, registry, classes)
    monkeypatch.setenv("WORKSPACE_HUB", "/checkout/two")
    second = generator.build(catalog, registry, classes)

    assert first == second


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


def test_digest_logical_names_are_posix_stable():
    generator = load_generator()
    relative = Path("scripts") / "cron" / "build-cron-identity-inventory.py"
    assert generator.digest_logical_name(ROOT / relative) == relative.as_posix()


def test_stale_inventory_diagnostic_reads_existing_digest():
    generator = load_generator()
    assert generator.rendered_input_digest(b'{"input_digest":"abc"}\n') == "abc"
    assert generator.rendered_input_digest(b"not-json") == "<invalid-json>"


def test_inventory_mismatch_summary_names_first_changed_row():
    generator = load_generator()
    current = b'{"collisions":[],"identities":[{"task_id":"old"}],"input_digest":"d","machines":[],"schema_version":1,"unsupported":[]}\n'
    generated = b'{"collisions":[],"identities":[{"task_id":"new"}],"input_digest":"d","machines":[],"schema_version":1,"unsupported":[]}\n'
    assert "identities[0]" in generator.inventory_mismatch_summary(current, generated)


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
