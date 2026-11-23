from pathlib import Path

import pytest

from registry import RegistryError, load_registry


def test_registry_parses_valid_yaml(fixture_registry):
    registry = load_registry(fixture_registry)

    assert len(registry.indexes) == 5
    assert registry.alias_map["/legacy/dde"] == "/canonical/dde"
    assert {index.id for index in registry.indexes} == {
        "fixture_sqlite",
        "fixture_jsonl",
        "fixture_tsv",
        "fixture_yaml",
        "fixture_missing",
    }


def test_registry_rejects_unknown_adapter(fixture_registry, tmp_path):
    text = Path(fixture_registry).read_text()
    bad = tmp_path / "bad.yml"
    bad.write_text(text.replace("adapter: jsonl", "adapter: parquet", 1))

    with pytest.raises(RegistryError, match="fixture_jsonl.*parquet"):
        load_registry(bad)


def test_registry_rejects_duplicate_ids(fixture_registry, tmp_path):
    text = Path(fixture_registry).read_text()
    bad = tmp_path / "bad.yml"
    bad.write_text(text.replace("id: fixture_jsonl", "id: fixture_sqlite", 1))

    with pytest.raises(RegistryError, match="duplicate.*fixture_sqlite"):
        load_registry(bad)


def test_registry_rejects_missing_required_key(fixture_registry, tmp_path):
    text = Path(fixture_registry).read_text()
    bad = tmp_path / "bad.yml"
    bad.write_text(text.replace("    path: fixtures/fixture.tsv\n", "", 1))

    with pytest.raises(RegistryError, match="fixture_tsv.*path"):
        load_registry(bad)


def test_registry_resolves_relative_paths(fixture_registry):
    registry = load_registry(fixture_registry)
    jsonl = registry.get("fixture_jsonl")

    assert jsonl.path.is_absolute()
    assert jsonl.path.name == "fixture.jsonl"
