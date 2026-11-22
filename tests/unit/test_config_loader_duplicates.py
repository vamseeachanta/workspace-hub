"""Regression tests for duplicate keys through the public load interface.

Expected mappings are read directly from the literal YAML examples below;
merge examples combine disjoint keys unless explicitly marked as collisions.
"""

import pytest
import yaml

from src.config.config_loader import ConfigLoader


def assert_rejected_before_caching(tmp_path, source, match="duplicate key"):
    """A rejected file must never become a cached configuration."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(source, encoding="utf-8")
    loader = ConfigLoader()

    with pytest.raises(yaml.YAMLError, match=match):
        loader.load(config_file)

    assert loader._cache == {}
    return config_file, loader


def test_duplicate_root_key_rejected(tmp_path):
    config_file, loader = assert_rejected_before_caching(
        tmp_path, "setting: original\nsetting: replacement\n"
    )
    config_file.write_text("setting: corrected\n", encoding="utf-8")
    assert loader.load(config_file) == {"setting": "corrected"}


@pytest.mark.parametrize(
    "source",
    [
        "section:\n  setting: original\n  setting: replacement\n",
        "sections:\n  - setting: original\n    setting: replacement\n",
    ],
    ids=["nested-mapping", "mapping-in-sequence"],
)
def test_duplicate_nested_key_rejected(tmp_path, source):
    assert_rejected_before_caching(tmp_path, source)


@pytest.mark.parametrize(
    "source",
    [
        "defaults: &defaults {setting: original}\n"
        "section: {<<: *defaults, setting: replacement}\n",
        "defaults: &defaults {setting: original}\n"
        "section: {setting: replacement, <<: *defaults}\n",
        "first: &first {setting: original}\n"
        "second: &second {setting: replacement}\n"
        "section: {<<: [*first, *second]}\n",
        "section: {<<: {setting: original}, setting: replacement}\n",
        "defaults: &defaults {setting: original}\n"
        "middle: &middle {<<: *defaults}\n"
        "section: {<<: *middle, setting: replacement}\n",
        "defaults: &defaults {setting: original}\n"
        "section: {<<: [*defaults, *defaults]}\n",
    ],
    ids=[
        "explicit-after-merge",
        "explicit-before-merge",
        "merge-sequence-collision",
        "inline-merge",
        "chained-merge",
        "repeated-alias",
    ],
)
def test_merge_override_rejected(tmp_path, source):
    assert_rejected_before_caching(tmp_path, source)


def test_duplicate_merge_directive_rejected(tmp_path):
    assert_rejected_before_caching(
        tmp_path,
        "section: {<<: {left: original}, <<: {right: replacement}}\n",
    )


@pytest.mark.parametrize("cache_enabled", [True, False])
def test_unique_keys_and_disjoint_merges_load(tmp_path, cache_enabled):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "left: &left {left: original}\n"
        "right: &right {right: replacement}\n"
        "section: {<<: [*left, *right], local: retained}\n"
        "literal: {'<<': ordinary}\n",
        encoding="utf-8",
    )
    loader = ConfigLoader(cache_enabled=cache_enabled)
    config = loader.load(config_file)

    assert config == {
        "left": {"left": "original"},
        "right": {"right": "replacement"},
        "section": {
            "left": "original",
            "right": "replacement",
            "local": "retained",
        },
        "literal": {"<<": "ordinary"},
    }
    if cache_enabled:
        assert loader.load(config_file) is config
    else:
        assert loader._cache == {}


def test_unsafe_object_tag_rejected(tmp_path):
    assert_rejected_before_caching(
        tmp_path,
        "setting: !!python/object/apply:builtins.str [unexpected]\n",
        match="could not determine a constructor",
    )


def test_unhashable_key_raises_yaml_error(tmp_path):
    assert_rejected_before_caching(
        tmp_path, "? [unhashable]\n: value\n", match="unhashable key"
    )


def test_empty_file_preserves_empty_mapping(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("", encoding="utf-8")
    assert ConfigLoader().load(config_file) == {}


def test_global_safe_load_behavior_unchanged(tmp_path):
    source = "setting: original\nsetting: replacement\n"
    assert_rejected_before_caching(tmp_path, source)
    assert yaml.safe_load(source) == {"setting": "replacement"}


@pytest.mark.parametrize(
    "source",
    [
        "true: original\nyes: replacement\n",
        "1: original\n0x1: replacement\n",
        ".nan: original\n.NaN: replacement\n",
        "null: original\n~: replacement\n",
    ],
    ids=["boolean", "integer", "nan", "null"],
)
def test_duplicate_resolved_scalar_key_rejected(tmp_path, source):
    assert_rejected_before_caching(tmp_path, source)


def test_distinct_typed_keys_load(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text('1: numeric\n"1": text\n', encoding="utf-8")

    assert ConfigLoader().load(config_file) == {1: "numeric", "1": "text"}


def test_recursive_alias_loads(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("section: &section {self: *section}\n", encoding="utf-8")

    config = ConfigLoader().load(config_file)

    assert set(config) == {"section"}
    assert set(config["section"]) == {"self"}
    assert config["section"]["self"] is config["section"]


def test_disjoint_chained_merges_load(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "base: &base {left: original}\n"
        "middle: &middle {<<: *base, right: replacement}\n"
        "section: {<<: *middle, local: retained}\n",
        encoding="utf-8",
    )

    assert ConfigLoader().load(config_file) == {
        "base": {"left": "original"},
        "middle": {"left": "original", "right": "replacement"},
        "section": {
            "left": "original",
            "right": "replacement",
            "local": "retained",
        },
    }
