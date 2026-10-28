"""Synthetic fixtures and independent byte oracles: docs/examples/algorithm-run-identity.md."""

from copy import deepcopy
from decimal import Decimal
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/algorithm_runs/identity_example.py"
SPEC = importlib.util.spec_from_file_location("identity_example", EXAMPLE)
example = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(example)

# Hand-constructed, lexically sorted UTF-8 JSON; no serializer under test is used.
VERSION_BYTES = (
    b'{"algorithm_id":"synthetic:counter","clean_git_commit":'
    b'"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","environment_digest":'
    b'"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",'
    b'"input_schema_version":"1.0.0","output_schema_version":"1.0.0",'
    b'"semantic_version":"1.0.0"}'
)
RUN_BYTES = (
    b'{"algorithm_version_id":"sha256:'
    b'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",'
    b'"execution_parameters":{"iterations":3,"label":"caf\xc3\xa9"},'
    b'"input_set_id":"sha256:'
    b'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",'
    b'"seed":7}'
)


@pytest.fixture
def record():
    # All numbers and fabricated pins are defined in the cited worked fixture.
    return {
        "algorithm_version": {
            "algorithm_id": "synthetic:counter",
            "semantic_version": "1.0.0",
            "clean_git_commit": "a" * 40,
            "input_schema_version": "1.0.0",
            "output_schema_version": "1.0.0",
            "environment_digest": "sha256:" + "b" * 64,
        },
        "input_set_id": "sha256:" + "d" * 64,
        "execution_parameters": {"iterations": 3, "label": "caf\u00e9"},
        "seed": 7,
        "observed_at": "2026-01-01T00:00:00Z",
    }


def test_identity_canonical_bytes_match_literal_oracle(record):
    assert example.canonical_bytes(record["algorithm_version"]) == VERSION_BYTES
    payload = {
        "algorithm_version_id": "sha256:" + "c" * 64,
        "input_set_id": record["input_set_id"],
        "execution_parameters": record["execution_parameters"],
        "seed": record["seed"],
    }
    assert example.canonical_bytes(payload) == RUN_BYTES
    for kind, value, literal in (
        ("algorithm_version_id", record["algorithm_version"], VERSION_BYTES),
        ("run_id", payload, RUN_BYTES),
    ):
        prefix = (kind + "\nidentity-jcs-1\n").encode("ascii")
        expected = "sha256:" + hashlib.sha256(prefix + literal).hexdigest()
        assert example.identity_digest(kind, value) == expected


def test_run_identity_matches_independent_projection_oracle(record):
    version_id = "sha256:" + hashlib.sha256(
        b"algorithm_version_id\nidentity-jcs-1\n" + VERSION_BYTES
    ).hexdigest()
    # Substitute only the independent version digest into the literal run bytes.
    literal_run = RUN_BYTES.replace(b"c" * 64, version_id.removeprefix("sha256:").encode())
    expected = "sha256:" + hashlib.sha256(
        b"run_id\nidentity-jcs-1\n" + literal_run
    ).hexdigest()
    assert example.algorithm_version_identity(record["algorithm_version"]) == version_id
    assert example.run_identity(record) == expected


def test_scheme_version_is_current_contract_version_not_document_version():
    contract = yaml.safe_load(
        (ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml").read_text()
    )
    assert example.CANONICALIZATION_VERSION == contract["identity"]["canonicalization"]["version"]
    assert example.CANONICALIZATION_VERSION != contract["contract_version"]


def test_key_reordering_is_same_identity(record):
    reordered = dict(reversed(list(record.items())))
    reordered["algorithm_version"] = dict(reversed(list(record["algorithm_version"].items())))
    reordered["execution_parameters"] = dict(reversed(list(record["execution_parameters"].items())))
    assert example.run_identity(reordered) == example.run_identity(record)


def test_unchanged_input_is_same_identity_without_mutation(record):
    before = deepcopy(record)
    assert example.run_identity(record) == example.run_identity(deepcopy(record))
    assert record == before


@pytest.mark.parametrize(("section", "field", "replacement"), [
    ("algorithm_version", "algorithm_id", "synthetic:other"),
    ("algorithm_version", "semantic_version", "2.0.0"),
    ("algorithm_version", "clean_git_commit", "e" * 40),
    ("algorithm_version", "input_schema_version", "2.0.0"),
    ("algorithm_version", "output_schema_version", "2.0.0"),
    ("algorithm_version", "environment_digest", "sha256:" + "e" * 64),
    (None, "input_set_id", "sha256:" + "e" * 64),
    (None, "seed", 8),
    ("execution_parameters", "iterations", 4),
    ("execution_parameters", "label", "tea"),
])
def test_identity_binding_field_changes_identity(record, section, field, replacement):
    changed = deepcopy(record)
    (changed if section is None else changed[section])[field] = replacement
    assert example.run_identity(changed) != example.run_identity(record)


def test_observation_time_does_not_change_identity(record):
    changed = deepcopy(record)
    changed["observed_at"] = "2026-01-02T00:00:00Z"
    changed["algorithm_version"]["observed_at"] = changed["observed_at"]
    assert example.run_identity(changed) == example.run_identity(record)
    del changed["observed_at"]
    assert example.run_identity(changed) == example.run_identity(record)


def test_outputs_and_extra_metadata_do_not_enter_projection(record):
    changed = deepcopy(record)
    changed["output_set_id"] = "sha256:" + "e" * 64
    changed["algorithm_version"]["description"] = "annotation"
    assert example.run_identity(changed) == example.run_identity(record)


def test_missing_revision_is_rejected(record):
    del record["algorithm_version"]["clean_git_commit"]
    with pytest.raises(ValueError, match="clean_git_commit"):
        example.run_identity(record)


@pytest.mark.parametrize("field", [
    "algorithm_id", "semantic_version", "input_schema_version",
    "output_schema_version", "environment_digest",
])
def test_missing_version_binding_is_rejected(record, field):
    del record["algorithm_version"][field]
    with pytest.raises(ValueError, match=field):
        example.run_identity(record)


@pytest.mark.parametrize("field", ["input_set_id", "execution_parameters", "seed"])
def test_missing_replay_binding_is_rejected(record, field):
    del record[field]
    with pytest.raises(ValueError, match=field):
        example.run_identity(record)


@pytest.mark.parametrize("revision", [None, "", "unknown", "a" * 39, "g" * 40])
def test_invalid_revision_is_rejected(record, revision):
    record["algorithm_version"]["clean_git_commit"] = revision
    with pytest.raises(ValueError, match="clean_git_commit"):
        example.run_identity(record)


@pytest.mark.parametrize("value", [1.0, float("nan"), float("inf"), Decimal("1"),
                                  True, None, (1,), {1}, b"text", object()])
def test_unsupported_values_are_rejected(record, value):
    record["execution_parameters"]["invalid"] = value
    with pytest.raises(ValueError):
        example.run_identity(record)


@pytest.mark.parametrize("key", ["caf\u00e9", 1])
def test_non_ascii_or_non_string_keys_are_rejected(key):
    with pytest.raises(ValueError, match="ASCII"):
        example.canonical_bytes({key: 1})


def test_nfc_strings_and_ordered_arrays():
    # Literal UTF-8 and integer spellings, independently written from the fixture rules.
    assert example.canonical_bytes({"text": "cafe\u0301"}) == b'{"text":"caf\xc3\xa9"}'
    assert example.canonical_bytes([0, -1, "NA", [], {}]) == b'[0,-1,"NA",[],{}]'
    assert example.canonical_bytes([1, 2]) != example.canonical_bytes([2, 1])
    assert example.canonical_bytes({"text": "\n\"\\"}) == b'{"text":"\\n\\\"\\\\"}'
    with pytest.raises(ValueError):
        example.canonical_bytes("\ud800")


def test_identity_types_are_domain_separated():
    assert example.identity_digest("run_id", {}) != example.identity_digest("algorithm_version_id", {})
    with pytest.raises(ValueError):
        example.identity_digest("run_id\nother", {})


@pytest.mark.parametrize("seed", [True, None, 1.0, "implicit"])
def test_invalid_seed_is_rejected(record, seed):
    record["seed"] = seed
    with pytest.raises(ValueError, match="seed"):
        example.run_identity(record)


def test_explicit_no_seed_is_supported(record):
    record["seed"] = "deterministic:no-seed"
    assert example.run_identity(record) == example.run_identity(deepcopy(record))


def test_offline_entry_point_emits_only_synthetic_identities(record):
    result = subprocess.run(
        [sys.executable, str(EXAMPLE)], check=True, capture_output=True, text=True,
        cwd=ROOT,
    )
    expected = (
        "algorithm_version_id=" + example.algorithm_version_identity(record["algorithm_version"])
        + "\nrun_id=" + example.run_identity(record) + "\n"
    )
    assert result.stdout == expected
    assert result.stderr == ""
