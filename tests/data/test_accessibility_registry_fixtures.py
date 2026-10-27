"""Synthetic fixtures for the existing accessibility registry contract.

Scope: issue #2156, structural validation only; no real registry payloads.
The schema version example is from issue #2136's implementation summary.
Diagnostic indices are hand-counted: the first asset is 0, the duplicate is 1.
Expected diagnostics are literal assertions, independent of validator constants.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def registry_fixture(tmp_path, monkeypatch):
    script = (
        Path(__file__).resolve().parent.parent.parent
        / "scripts"
        / "data"
        / "document-index"
        / "validate-accessibility-registry.py"
    )
    spec = importlib.util.spec_from_file_location("accessibility_validator", script)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)

    root = tmp_path / "repository"
    root.mkdir()
    monkeypatch.setattr(validator, "REPO_ROOT", root)
    # Registry location and current directory deliberately differ from the root.
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    monkeypatch.chdir(inputs)
    target = root / "content" / "asset.md"
    target.parent.mkdir()
    target.write_text("Synthetic registry target.\n", encoding="utf-8")
    data = {
        "generated": "synthetic-fixture",
        "schema_version": "1.0.0",
        "assets": [
            {
                "asset_key": "fixture-asset",
                "title": "Fixture asset",
                "asset_type": "registry",
                "layer": "L2",
                "canonical_path": target.relative_to(root).as_posix(),
                "machine_scope": ["all-git-clones"],
                "source_of_truth_tier": "git-tracked",
                "durability": "durable",
            }
        ],
    }
    return validator, inputs / "registry.yaml", data, root


def _validate_fixture(validator, registry_path, data):
    registry_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return validator.validate(registry_path)


@pytest.mark.parametrize("target_kind", ["file", "directory"])
def test_minimal_registry_fixture_is_valid(registry_fixture, target_kind):
    validator, registry_path, data, root = registry_fixture
    entry, = data["assets"]
    target = root / entry["canonical_path"]
    if target_kind == "directory":
        entry["canonical_path"] = target.parent.relative_to(root).as_posix()
        target = target.parent

    assert not Path(entry["canonical_path"]).is_absolute()
    assert target.resolve().is_relative_to(root.resolve())
    assert target.exists()
    assert _validate_fixture(validator, registry_path, data) == []


def test_duplicate_asset_key(registry_fixture):
    validator, registry_path, data, _ = registry_fixture
    entry, = data["assets"]
    data["assets"].append(dict(entry))

    assert _validate_fixture(validator, registry_path, data) == [
        "assets[1] (fixture-asset): duplicate asset_key 'fixture-asset'"
    ]


@pytest.mark.parametrize("field", ["generated", "schema_version"])
def test_missing_header_metadata(registry_fixture, field):
    validator, registry_path, data, _ = registry_fixture
    del data[field]

    assert _validate_fixture(validator, registry_path, data) == [
        f"Missing top-level field: {field}"
    ]


@pytest.mark.parametrize(
    "field",
    [
        "asset_key",
        "title",
        "asset_type",
        "layer",
        "canonical_path",
        "machine_scope",
        "source_of_truth_tier",
        "durability",
    ],
)
@pytest.mark.parametrize("state", ["absent", "null", "blank"])
def test_missing_required_metadata(registry_fixture, field, state):
    validator, registry_path, data, _ = registry_fixture
    entry, = data["assets"]
    if state == "absent":
        del entry[field]
    else:
        entry[field] = None if state == "null" else "   "
    key = entry.get("asset_key", "<missing-key-0>")

    errors = _validate_fixture(validator, registry_path, data)

    assert f"assets[0] ({key}): missing required field '{field}'" in errors


@pytest.mark.parametrize(
    "field",
    ["asset_type", "layer", "source_of_truth_tier", "durability", "discoverability"],
)
def test_invalid_enum(registry_fixture, field):
    validator, registry_path, data, _ = registry_fixture
    entry, = data["assets"]
    entry[field] = "invalid-fixture-value"

    error, = _validate_fixture(validator, registry_path, data)

    assert error.startswith(
        f"assets[0] (fixture-asset): invalid {field} 'invalid-fixture-value' (valid: "
    )


def test_missing_canonical_target(registry_fixture):
    validator, registry_path, data, root = registry_fixture
    entry, = data["assets"]
    target = root / "missing" / "asset.md"
    relative = target.relative_to(root)
    entry["canonical_path"] = relative.as_posix()
    # A same-named target beside the YAML must not satisfy root-relative lookup.
    decoy = registry_path.parent / relative
    decoy.parent.mkdir()
    decoy.write_text("Synthetic decoy.\n", encoding="utf-8")
    assert not target.exists()

    assert _validate_fixture(validator, registry_path, data) == [
        f"assets[0] (fixture-asset): canonical_path does not exist: {relative.as_posix()}"
    ]


@pytest.mark.parametrize("scope", [[], "all-git-clones"])
def test_machine_scope_requires_nonempty_list(registry_fixture, scope):
    validator, registry_path, data, _ = registry_fixture
    entry, = data["assets"]
    entry["machine_scope"] = scope

    assert _validate_fixture(validator, registry_path, data) == [
        "assets[0] (fixture-asset): machine_scope must be a non-empty list"
    ]
