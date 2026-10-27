"""Synthetic adapter examples; expected totals are hand-counted below.

Schema and enum literals follow the existing accessibility validator and
data/document-index/intelligence-accessibility-registry.yaml. Dates and evidence
references are synthetic declarations, not observations about real inventories.
"""

from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

# Two parent levels above tests/knowledge locate the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/knowledge/seed_accessibility_registry.py"
VALIDATOR = REPO_ROOT / "scripts/data/document-index/validate-accessibility-registry.py"
GENERATED = "2026-01-01T00:00:00Z"


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def seeder():
    return load_module(SCRIPT)


@pytest.fixture
def rows(tmp_path):
    """Hand count: one map plus one registry equals two distinct assets."""
    (tmp_path / "maps").mkdir()
    (tmp_path / "maps/example.md").write_text("Synthetic map\n", encoding="utf-8")
    (tmp_path / "catalog").mkdir()
    return [
        {
            "asset_key": "example-registry",
            "title": "Example registry",
            "asset_type": "registry",
            "layer": "L2",
            "canonical_path": "catalog/",
            "machine_scope": ["all-git-clones"],
            "source_of_truth_tier": "git-tracked",
            "durability": "durable",
            "source_ref": "inventories/example.yaml#example-registry",
            "provenance": "Declared by the synthetic inventory example",
            "discoverability": "partially-discoverable",
        },
        {
            "asset_key": "example-map",
            "title": "Example map",
            "asset_type": "map",
            "layer": "L4",
            "canonical_path": "maps/example.md",
            "machine_scope": ["all-git-clones"],
            "source_of_truth_tier": "git-tracked",
            "durability": "durable",
            "source_ref": "inventories/example.yaml#example-map",
            "provenance": "Declared by the synthetic map example",
            "human_entry_point": "maps/example.md",
        },
    ]


def test_seed_rows_preserve_identity_and_provenance(seeder, rows, tmp_path):
    original = copy.deepcopy(rows)
    document = yaml.safe_load(seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path))
    assert document["generated"] == GENERATED
    # Existing registry header declares this schema version.
    assert document["schema_version"] == "1.1.3"
    assert len(document["assets"]) == 2  # One map + one registry, counted above.
    assert document["assets"] == [original[1], original[0]]
    assert rows == original


def test_seed_output_passes_existing_validator(seeder, rows, tmp_path, monkeypatch):
    validator = load_module(VALIDATOR)
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    registry = tmp_path / "generated.yaml"
    registry.write_text(seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path))
    assert validator.validate(registry) == []


def test_seed_reordered_input_is_byte_identical(seeder, rows, tmp_path):
    expected = seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)
    reordered = [dict(reversed(list(row.items()))) for row in reversed(rows)]
    assert seeder.seed_registry(reordered, generated=GENERATED, repo_root=tmp_path) == expected
    assert seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path) == expected


def test_seed_duplicate_key_refused(seeder, rows, tmp_path):
    rows.append(copy.deepcopy(rows[0]))
    with pytest.raises(ValueError, match="duplicate asset_key"):
        seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)


@pytest.mark.parametrize("field", [
    "asset_key", "title", "asset_type", "layer", "canonical_path", "machine_scope",
    "source_of_truth_tier", "durability", "source_ref", "provenance",
])
@pytest.mark.parametrize("missing", [True, False], ids=["absent", "blank"])
def test_seed_incomplete_row_refused(seeder, rows, tmp_path, field, missing):
    if missing:
        del rows[0][field]
    else:
        rows[0][field] = " "
    with pytest.raises(ValueError, match=field):
        seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)


@pytest.mark.parametrize("field,value", [
    ("asset_key", "Example map"),
    ("asset_key", "example-map\n"),
    ("asset_key", True),
    ("canonical_path", "../outside"),
    ("canonical_path", "missing.md"),
    ("machine_scope", []),
    ("machine_scope", [None]),
    ("source_ref", []),
    ("provenance", False),
    ("asset_type", "unrecognized"),
    ("layer", "unrecognized"),
    ("source_of_truth_tier", "unrecognized"),
    ("durability", "unrecognized"),
    ("discoverability", "unrecognized"),
    ("discoverability", ["discoverable"]),
    ("discoverability", True),
])
def test_seed_invalid_metadata_refused(seeder, rows, tmp_path, field, value):
    rows[0][field] = value
    with pytest.raises(ValueError, match=field):
        seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)


def test_seed_absolute_path_refused(seeder, rows, tmp_path):
    rows[0]["canonical_path"] = str(tmp_path / "catalog")
    with pytest.raises(ValueError, match="canonical_path"):
        seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)


@pytest.mark.parametrize("value", ["", " ", None, "not-a-time", "2026-01-01T00:00:00"])
def test_seed_requires_supplied_generation_time(seeder, rows, tmp_path, value):
    with pytest.raises(ValueError, match="generated"):
        seeder.seed_registry(rows, generated=value, repo_root=tmp_path)


@pytest.mark.parametrize("value", [[], {}, [None]])
def test_seed_invalid_inventory_refused(seeder, tmp_path, value):
    with pytest.raises(ValueError, match="rows"):
        seeder.seed_registry(value, generated=GENERATED, repo_root=tmp_path)


def test_seed_reordered_nested_metadata_is_byte_identical(seeder, rows, tmp_path):
    rows[0]["fields"] = [{"name": "example", "type": "string"}]
    expected = seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)
    rows[0]["fields"] = [{"type": "string", "name": "example"}]
    assert seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path) == expected


@pytest.mark.parametrize("problem", ["mixed-keys", "cycle"])
def test_seed_ambiguous_nested_metadata_refused(seeder, rows, tmp_path, problem):
    if problem == "mixed-keys":
        rows[0]["fields"] = {"name": "example", False: "ambiguous"}
    else:
        rows[0]["fields"] = rows[0]
    with pytest.raises(ValueError, match="metadata"):
        seeder.seed_registry(rows, generated=GENERATED, repo_root=tmp_path)


def invoke_cli(tmp_path, inventory, *extra):
    # Fixture subprocesses must not inherit bindings to another Git checkout.
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory", str(inventory),
         "--output", str(tmp_path / "generated.yaml"), "--repo-root", str(tmp_path), *extra],
        capture_output=True, text=True, env=env, check=False,
    )


def test_cli_seeds_only_supplied_rows(rows, tmp_path):
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(yaml.safe_dump({"rows": rows}), encoding="utf-8")
    # An unrelated file is not an inventory row.
    (tmp_path / "unlisted.md").write_text("Unlisted\n", encoding="utf-8")
    result = invoke_cli(tmp_path, inventory, "--generated", GENERATED)
    assert result.returncode == 0, result.stderr
    output = (tmp_path / "generated.yaml").read_bytes()
    document = yaml.safe_load(output)
    assert document["assets"] == sorted(rows, key=lambda row: row["asset_key"])
    inventory.write_text(yaml.safe_dump({"rows": rows[::-1]}), encoding="utf-8")
    assert invoke_cli(tmp_path, inventory, "--generated", GENERATED).returncode == 0
    assert (tmp_path / "generated.yaml").read_bytes() == output


def test_cli_requires_time(rows, tmp_path):
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(yaml.safe_dump({"rows": rows}), encoding="utf-8")
    result = invoke_cli(tmp_path, inventory)
    assert result.returncode != 0
    assert "--generated" in result.stderr
    assert not (tmp_path / "generated.yaml").exists()


def test_cli_refuses_output_over_inventory(rows, tmp_path):
    inventory = tmp_path / "generated.yaml"
    original = yaml.safe_dump({"rows": rows}).encode("utf-8")
    inventory.write_bytes(original)
    result = invoke_cli(tmp_path, inventory, "--generated", GENERATED)
    assert result.returncode != 0
    assert "output must differ from inventory" in result.stderr
    assert inventory.read_bytes() == original


@pytest.mark.parametrize("problem", ["missing-provenance", "duplicate-field", "wrong-root"])
def test_cli_invalid_input_preserves_output(rows, tmp_path, problem):
    inventory = tmp_path / "inventory.yaml"
    output = tmp_path / "generated.yaml"
    output.write_bytes(b"Existing output\n")
    if problem == "missing-provenance":
        del rows[0]["provenance"]
        text = yaml.safe_dump({"rows": rows})
    elif problem == "duplicate-field":
        text = yaml.safe_dump({"rows": rows}) + "rows: []\n"
    else:
        text = yaml.safe_dump({"assets": rows})
    inventory.write_text(text, encoding="utf-8")
    result = invoke_cli(tmp_path, inventory, "--generated", GENERATED)
    assert result.returncode != 0
    expected_error = {"missing-provenance": "provenance",
                      "duplicate-field": "duplicate", "wrong-root": "rows"}[problem]
    assert expected_error in result.stderr
    assert output.read_bytes() == b"Existing output\n"
