"""Offline structural checks for the smoke-battery contract; no execution.

Format choices and rejection cases are specified in
docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md, "Battery format" and
"Path boundary". Valid values come from the committed synthetic example.
"""

import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "config/ai/model-release-smoke-battery.schema.json"
EXAMPLE = ROOT / "config/ai/model-release-smoke-battery.example.yaml"
CONTRACT = ROOT / "docs/standards/MODEL_RELEASE_SMOKE_RUNNER_CONTRACT.md"


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    # All references are local; validation requires no network or adapter.
    return Draft202012Validator(schema)


@pytest.fixture
def battery():
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def _at(document, path):
    for key in path:
        document = document[key]
    return document


def _replace(document, path, value):
    _at(document, path[:-1])[path[-1]] = value


# Case index zero selects the sole synthetic case in the cited example.
REQUIRED_FIELDS = [
    ("schema_version",),
    ("battery_id",),
    ("fixture_root",),
    ("execution",),
    ("execution", "interface"),
    ("execution", "adapter_id"),
    ("cases",),
    ("cases", 0, "case_id"),
    ("cases", 0, "input_ref"),
    ("cases", 0, "expected_result_ref"),
]
PATH_FIELDS = [
    ("fixture_root",),
    ("cases", 0, "input_ref"),
    ("cases", 0, "expected_result_ref"),
]


def test_documented_example_validates(validator, battery):
    validator.validate(battery)
    text = CONTRACT.read_text(encoding="utf-8")
    assert SCHEMA.name in text
    assert EXAMPLE.name in text


@pytest.mark.parametrize("value", [None, [], "battery", True])
def test_nonobject_batteries_are_rejected(validator, value):
    assert not validator.is_valid(value)


@pytest.mark.parametrize("path", REQUIRED_FIELDS)
def test_missing_required_fields_are_rejected(validator, battery, path):
    del _at(battery, path[:-1])[path[-1]]
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path", REQUIRED_FIELDS)
def test_null_fields_are_rejected(validator, battery, path):
    _replace(battery, path, None)
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path,value", [
    (("schema_version",), "1"),
    (("schema_version",), True),
    (("battery_id",), []),
    (("fixture_root",), {}),
    (("execution",), "adapter-v1"),
    (("execution", "interface"), []),
    (("execution", "adapter_id"), False),
    (("cases",), {}),
    (("cases",), ["case"]),
    (("cases", 0, "case_id"), {}),
    (("cases", 0, "input_ref"), []),
    (("cases", 0, "expected_result_ref"), False),
])
def test_wrong_types_are_rejected(validator, battery, path, value):
    _replace(battery, path, value)
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path", [(), ("execution",), ("cases", 0)])
def test_unknown_keys_are_rejected(validator, battery, path):
    # A command must never become an execution path through this format.
    _at(battery, path)["command"] = "synthetic-command"
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path", PATH_FIELDS)
@pytest.mark.parametrize("value", [
    "", ".", "..", "../outside.txt", "fixtures/../outside.txt",
    "fixtures/./input.txt", "fixtures//input.txt", "fixtures/",
    "fixtures/..", "fixtures/.", "//fixtures/input.txt",
    "C:/fixtures/input.txt", "C:input.txt", "fixtures\\input.txt",
    "https://example.invalid/input.txt", "file:input.txt",
    "%2e%2e/input.txt", "fixtures/%2finput.txt", "~/input.txt",
    "fixtures/input.txt\n", "fixtures/input.txt\r", "fixtures/\x00input.txt",
    "fixtures/ input.txt", "fixtures/input.txt ", "fixtures/input.txt:stream",
    "fixtures/input.", "${FIXTURES}/input.txt",
])
def test_escaping_or_nonportable_paths_are_rejected(validator, battery, path, value):
    _replace(battery, path, value)
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path", PATH_FIELDS)
def test_absolute_paths_are_rejected(validator, battery, tmp_path, path):
    # Construct platform-native absolute paths without embedding local paths.
    _replace(battery, path, str(tmp_path / "input.txt"))
    assert not validator.is_valid(battery)


@pytest.mark.parametrize("path", PATH_FIELDS)
@pytest.mark.parametrize("value", ["input.txt", "nested/expected-result_v1.json"])
def test_portable_relative_paths_are_accepted(validator, battery, path, value):
    _replace(battery, path, value)
    validator.validate(battery)


@pytest.mark.parametrize("path", [
    ("battery_id",), ("execution", "adapter_id"), ("cases", 0, "case_id"),
])
@pytest.mark.parametrize("value", ["", " ", "../case", "case\n", "Case"])
def test_invalid_identities_are_rejected(validator, battery, path, value):
    _replace(battery, path, value)
    assert not validator.is_valid(battery)


def test_empty_battery_is_rejected(validator, battery):
    battery["cases"] = []
    assert not validator.is_valid(battery)


def test_duplicate_case_objects_are_rejected(validator, battery):
    battery["cases"].append(copy.deepcopy(battery["cases"][0]))
    assert not validator.is_valid(battery)


def test_undeclared_schema_version_is_rejected(validator, battery):
    # The declared identifier is fixed; adding one produces an unknown identifier.
    battery["schema_version"] += 1
    assert not validator.is_valid(battery)


def test_undeclared_execution_interface_is_rejected(validator, battery):
    battery["execution"]["interface"] = "shell"
    assert not validator.is_valid(battery)


def test_schema_references_are_local():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "$ref":
                    assert item.startswith("#/$defs/")
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(schema)


def test_runner_contract_is_discoverable():
    for name in (
        "AGENTS.md",
        "docs/standards/CONTROL_PLANE_CONTRACT.md",
        "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md",
        "docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md",
    ):
        assert CONTRACT.name in (ROOT / name).read_text(encoding="utf-8")
