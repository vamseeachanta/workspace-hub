"""Task 2 deterministic cron identity inventory tests."""
from __future__ import annotations

import json
import hashlib
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
    path.write_text(yaml.safe_dump(value), encoding="utf-8", newline="\n")


def public_key(kind: str, value: str) -> str:
    return hashlib.sha256(f"cron-{kind}:{value}".encode()).hexdigest()[:12]


def projection_fixture(tmp_path):
    machines = {
        key: {"hostname": host, "hostname_aliases": [alias], "os": "linux",
              "workspace_root": (tmp_path / key).as_posix(),
              "harness_profile": {"roles": []}}
        for key, host, alias in (
            ("synthetic-alpha", "synthetic-host-alpha", "synthetic-alias-alpha"),
            ("synthetic-beta", "synthetic-host-beta", "synthetic-alias-beta"),
        )
    }
    labels = [label for key, row in machines.items()
              for label in (key, row["hostname"], *row["hostname_aliases"])]
    tasks = [{"id": f"task-{label}", "scheduler": "cron",
              "schedule": "0 1 * * *", "command": "echo shared",
              "machines": list(machines), "roles": []} for label in labels]
    classes = {"preserved_external": [], "preserved_local": [{
        "owner": "local", "catalog_task_id": task["id"],
        "legacy_exact_lines": [{"id": f"legacy-{label}",
                                "line": f"0 2 * * * echo legacy-{index}"}],
    } for index, (task, label) in enumerate(zip(tasks, labels))]}
    paths = [tmp_path / name for name in ("catalog.yaml", "registry.yaml", "classes.yaml")]
    for path, data in zip(paths, ({"tasks": tasks}, {"machines": machines}, classes)):
        write_yaml(path, data)
    return paths, machines, labels


def test_public_inventory_contains_no_registry_names_in_any_string(tmp_path):
    generator = load_generator()
    paths, _machines, labels = projection_fixture(tmp_path)
    raw = generator.render(generator.build(*paths)).decode()
    assert all(label not in raw for label in labels)


def test_public_machine_keys_are_stable_unique_and_canonical(tmp_path):
    generator = load_generator()
    paths, machines, _labels = projection_fixture(tmp_path)
    first = generator.build(*paths)
    assert generator.render(first) == generator.render(generator.build(*paths))
    expected = [public_key("machine", key) for key in sorted(machines)]
    assert first["machines"] == expected
    assert len(set(expected)) == len(machines)
    assert {row["machine_id"] for row in first["identities"]} == set(expected)
    # Adding a registry entry must not renumber existing machines or tasks.
    expanded = dict(machines)
    expanded["synthetic-gamma"] = {
        "hostname": "synthetic-host-gamma", "os": "linux",
        "workspace_root": (tmp_path / "gamma").as_posix(), "harness_profile": {"roles": []},
    }
    write_yaml(paths[1], {"machines": expanded})
    second = generator.build(*paths)
    assert second["identities"] == first["identities"]
    assert set(expected) < set(second["machines"])


# Independent vectors: OpenSSL `printf %s INPUT | openssl dgst -sha256`,
# with no newline in INPUT; take the first 12 hexadecimal digest characters.
# Inputs are the literal domain-prefixed strings shown below. Expected rows
# are enumerated by hand: two tasks share one exact line on one synthetic
# machine; only the first task has the declared legacy variant.
@pytest.mark.parametrize(("kind", "value", "expected"), [
    ("machine", "synthetic-alpha", "dd1e55cf4a15"),
    ("task", "first", "f973414233d7"),
    ("task", "second", "42f684a9dec6"),
    ("legacy", "previous", "5559690bad68"),
])
def test_fixed_openssl_key_vectors(kind, value, expected):
    assert load_generator()._opaque_key(kind, value) == expected


def test_projection_preserves_canonical_ownership_legacy_and_collisions(tmp_path):
    generator = load_generator()
    paths = [tmp_path / name for name in ("catalog.yaml", "registry.yaml", "classes.yaml")]
    write_yaml(paths[0], {"tasks": [
        {"id": task, "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo shared", "machines": ["synthetic-alpha"], "roles": []}
        for task in ("first", "second")
    ]})
    write_yaml(paths[1], {"machines": {"synthetic-alpha": {
        "os": "linux", "workspace_root": tmp_path.as_posix(),
        "harness_profile": {"roles": []},
    }}})
    write_yaml(paths[2], {"preserved_external": [], "preserved_local": [{
        "owner": "local", "catalog_task_id": "first",
        "legacy_exact_lines": [{"id": "previous", "line": "0 2 * * * echo previous"}],
    }]})
    # OpenSSL hashes the literal UTF-8 bytes `0 1 * * * echo shared`,
    # without a newline. No production renderer or context supplies this oracle.
    line_digest = "a29c194d96f271388af22c094615f47230cba690f328028773e28a01d24db801"
    payload = generator.build(*paths)
    assert payload["machines"] == ["dd1e55cf4a15"]
    assert payload["identities"] == [
        {"machine_id": "dd1e55cf4a15", "task_id": "f973414233d7",
         "canonical_line_sha256": line_digest,
         "legacy_variant_ids": ["5559690bad68"], "unique": False},
        {"machine_id": "dd1e55cf4a15", "task_id": "42f684a9dec6",
         "canonical_line_sha256": line_digest,
         "legacy_variant_ids": [], "unique": False},
    ]
    assert payload["collisions"] == [{
        "machine_id": "dd1e55cf4a15",
        "task_ids": ["f973414233d7", "42f684a9dec6"],
        "line_sha256": line_digest,
    }]
    assert payload["unsupported"] == []


@pytest.mark.parametrize("kind", ["machine", "task", "legacy"])
def test_opaque_collisions_fail_closed_for_each_kind(tmp_path, monkeypatch, kind):
    generator = load_generator()
    paths, _machines, _labels = projection_fixture(tmp_path)
    original = generator._opaque_key
    monkeypatch.setattr(generator, "_opaque_key", lambda domain, value:
                        "000000000000" if domain == kind else original(domain, value))
    with pytest.raises(ValueError, match=f"opaque {kind} key collision"):
        generator.build(*paths)


def test_projection_covers_unbound_legacy_and_unsupported_errors(tmp_path, monkeypatch):
    generator = load_generator()
    paths, _machines, labels = projection_fixture(tmp_path)
    def unsupported(*args, **kwargs):
        raise ValueError("unsupported " + " ".join(labels))
    monkeypatch.setattr(generator, "build_ownership_context", unsupported)
    payload = generator.build(*paths)
    assert payload["unsupported"]
    assert all(label not in generator.render(payload).decode() for label in labels)
    unbound = [row for row in payload["unsupported"] if "variant_id" in row]
    assert len(unbound) == len(labels)
    assert {(row["task_id"], row["variant_id"]) for row in unbound} == {
        (public_key("task", "task-" + label), public_key("legacy", "legacy-" + label))
        for label in labels
    }


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
    assert payload["machines"] == [public_key("machine", "linux-a")]
    assert payload["unsupported"] == []
    assert payload["collisions"] == []
    assert first.endswith(b"\n")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode == 0
    catalog.write_text(catalog.read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="\n")
    assert subprocess.run(command + ["--check"], cwd=ROOT).returncode != 0


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
                            "task_id": public_key("task", "other"),
                            "variant_id": public_key("legacy", "old")}]


@pytest.mark.parametrize("malformed", [None, 7, ["not", "a", "mapping"]])
def test_malformed_state_classes_fail_without_traceback(tmp_path, malformed):
    task = {"id": "one", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "echo one", "machines": ["linux-a"], "roles": []}
    _catalog, state_classes, output, command = fixture_paths(tmp_path, [task])
    state_classes.write_text(yaml.safe_dump(malformed), encoding="utf-8", newline="\n")
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
    output.write_text("{}\n", encoding="utf-8", newline="\n")
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
