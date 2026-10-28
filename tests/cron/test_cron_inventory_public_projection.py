"""Public inventory projection must preserve canonical ownership decisions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/cron/build-cron-identity-inventory.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("public_inventory_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_key(kind, value):
    return kind + "-" + hashlib.sha256(f"cron-{kind}:{value}".encode()).hexdigest()


@pytest.fixture
def inputs(tmp_path):
    machines = {
        f"fixture-node-{suffix}": {
            "os": "linux", "hostname": f"fixture-host-{suffix}",
            "hostname_aliases": [f"fixture-alias-{suffix}"],
            "workspace_root": str(tmp_path / suffix / "checkout"),
            "harness_profile": {"roles": []},
        }
        for suffix in ("a", "b")
    }
    tasks = [
        {"id": "task-fixture-node-a", "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo shared", "machines": list(machines), "roles": []},
        {"id": "task-fixture-host-b", "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo shared", "machines": ["fixture-node-b"], "roles": []},
        {"id": "unbound-fixture-alias-a", "scheduler": "cron", "schedule": "0 1 * * *",
         "command": "echo unselected", "machines": ["elsewhere"], "roles": []},
    ]
    classes = {"preserved_external": [], "preserved_local": [
        {"owner": "fixture-node-a", "catalog_task_id": tasks[0]["id"],
         "legacy_exact_lines": [{"id": "legacy-fixture-alias-b",
                                 "line": "0 2 * * * echo legacy"}]},
        {"owner": "fixture-node-a", "catalog_task_id": tasks[2]["id"],
         "legacy_exact_lines": [{"id": "legacy-fixture-node-b",
                                 "line": "0 3 * * * echo unbound"}]},
    ]}
    documents = ({"tasks": tasks}, {"machines": machines}, classes)
    paths = [tmp_path / name for name in ("catalog.yaml", "registry.yaml", "classes.yaml")]
    for path, document in zip(paths, documents):
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
    return paths, documents


def test_no_registry_machine_labels_anywhere_in_public_inventory(inputs):
    paths, (_, registry, _) = inputs
    payload = load_generator().build(*paths)
    emitted = json.dumps(payload).casefold()
    for canonical, machine in registry["machines"].items():
        for label in (canonical, machine["hostname"], *machine["hostname_aliases"]):
            assert label.casefold() not in emitted


def test_public_keys_are_stable_distinct_and_independent_of_registry_order(inputs):
    paths, (_, registry, _) = inputs
    generator = load_generator()
    first = generator.build(*paths)
    assert generator.render(first) == generator.render(generator.build(*paths))
    assert first["machines"] == [public_key("machine", key) for key in sorted(registry["machines"])]
    assert len(set(first["machines"])) == len(registry["machines"])
    assert {row["machine_id"] for row in first["identities"]} == set(first["machines"])
    registry["machines"] = dict(reversed(list(registry["machines"].items())))
    paths[1].write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    reordered = generator.build(*paths)
    assert reordered["machines"] == first["machines"]
    assert reordered["identities"] == first["identities"]


def test_projection_preserves_ownership_legacy_binding_and_collision_results(inputs):
    paths, (catalog, registry, classes) = inputs
    generator = load_generator()
    # The pre-projection collector stays canonical. Compare all of its rows and
    # collision outcomes to the public result, allowing only identifier changes.
    rows, unsupported, collisions, bound = [], [], [], set()
    for machine in sorted(registry["machines"]):
        generator._build_machine(catalog, registry, classes, machine,
                                 rows, unsupported, collisions, bound)
    assert unsupported == []
    assert len(rows) == 3
    assert len(collisions) == 1
    assert len(bound) == 1
    expected_rows = [{
        **row, "machine_id": public_key("machine", row["machine_id"]),
        "task_id": public_key("task", row["task_id"]),
        "legacy_variant_ids": [public_key("legacy", item) for item in row["legacy_variant_ids"]],
    } for row in rows]
    expected_collisions = [{
        **row, "machine_id": public_key("machine", row["machine_id"]),
        "task_ids": [public_key("task", item) for item in row["task_ids"]],
    } for row in collisions]
    payload = generator.build(*paths)
    assert payload["identities"] == expected_rows
    assert payload["collisions"] == expected_collisions
    assert payload["unsupported"] == [{
        "error": "legacy variant is not bound in a canonical Linux context",
        "task_id": public_key("task", catalog["tasks"][2]["id"]),
        "variant_id": public_key("legacy", "legacy-fixture-node-b"),
    }]


def test_unsupported_diagnostics_do_not_emit_machine_labels(inputs, monkeypatch):
    paths, (_, registry, _) = inputs
    generator = load_generator()

    def reject(*args, **kwargs):
        labels = [label for key, row in registry["machines"].items()
                  for label in (key, row["hostname"], *row["hostname_aliases"])]
        raise ValueError("unsupported: " + " / ".join(labels).upper())

    monkeypatch.setattr(generator, "build_ownership_context", reject)
    payload = generator.build(*paths)
    assert len(payload["unsupported"]) == 4
    emitted = json.dumps(payload).casefold()
    for key, row in registry["machines"].items():
        for label in (key, row["hostname"], *row["hostname_aliases"]):
            assert label.casefold() not in emitted
