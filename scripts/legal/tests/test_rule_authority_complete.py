"""Authenticated COMPLETE transaction codec vectors."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import hashlib
import hmac
import importlib
import json
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, REVISION

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority.coverage_contract import REQUIRED_COVERAGE  # noqa: E402

COMPLETE_DOMAIN = b"LEGAL-RULE-COMPLETE\0v1\0"
EXPECTED_MAC = "1a47166e06269356ded12f0bc530951e1b4cb53c93ab07ff964c2289b4afdfe1"


def modules():
    return (importlib.import_module("rule_authority.codec"),
            importlib.import_module("rule_authority.complete"))


def unsigned_complete():
    return {
        "api_snapshot_id": "api-snapshot-synthetic",
        "authority_revision": REVISION,
        "coverage_states": {name: "scanned" for name in REQUIRED_COVERAGE},
        "files": [
            {"path": "coverage.json", "sha256": "a" * 64, "size": 42},
            {"path": "findings.bin", "sha256": "c" * 64, "size": 0},
            {"path": "reachability.json", "sha256": "d" * 64, "size": 84},
        ],
        "generation": 2,
        "manifest_mac": "b" * 64,
        "ref_snapshot_id": "ref-snapshot-synthetic",
        "schema_id": "legal-rule-complete-v1",
        "transaction_id": "423e4567-e89b-42d3-a456-426614174000",
    }


def test_complete_document_has_independent_golden_hmac_and_bytes():
    codec, complete = modules()
    unsigned = unsigned_complete()
    expected_input = COMPLETE_DOMAIN + codec.canonical_bytes(unsigned)
    expected_mac = hmac.new(KEY, expected_input, hashlib.sha256).hexdigest()
    document = complete.create_complete(unsigned, KEY)
    assert complete.complete_mac_input(unsigned) == expected_input
    assert expected_mac == EXPECTED_MAC
    assert document["complete_mac"] == expected_mac
    raw = codec.encode_document("complete", document)
    assert codec.decode_document("complete", raw) == document
    expected_document = {**unsigned, "complete_mac": EXPECTED_MAC}
    expected_raw = (json.dumps(
        expected_document, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ) + "\n").encode("ascii")
    assert raw == expected_raw
    assert complete.verify_complete(raw, KEY) == document


def test_complete_tamper_and_key_size_reject():
    codec, complete = modules()
    document = complete.create_complete(unsigned_complete(), KEY)
    document["files"][0]["size"] += 1
    with pytest.raises(complete.CompleteIntegrityError):
        complete.verify_complete(codec.encode_document("complete", document), KEY)
    with pytest.raises(complete.CompleteIntegrityError):
        complete.create_complete(unsigned_complete(), KEY[:-1])


class DerivedBytes(bytes):
    """A bytes subclass is not an exact bytes key."""


INVALID_COMPLETE_KEYS = (
    pytest.param(bytearray(KEY), id="bytearray"),
    pytest.param(memoryview(KEY), id="memoryview"),
    pytest.param("x" * 32, id="str"),
    pytest.param(None, id="none"),
    pytest.param(b"x", id="one-byte"),
    pytest.param(b"x" * 31, id="short"),
    pytest.param(b"x" * 33, id="long"),
    pytest.param(DerivedBytes(KEY), id="bytes-subclass"),
)


def _forbid_hmac(*_args, **_kwargs):
    raise AssertionError("invalid COMPLETE key reached HMAC")


@pytest.mark.parametrize("invalid_key", INVALID_COMPLETE_KEYS)
def test_create_complete_rejects_invalid_key_before_hmac(monkeypatch, invalid_key):
    _, complete = modules()
    monkeypatch.setattr(complete.hmac, "new", _forbid_hmac)
    with pytest.raises(complete.CompleteIntegrityError, match="invalid key"):
        complete.create_complete(unsigned_complete(), invalid_key)


@pytest.mark.parametrize("invalid_key", INVALID_COMPLETE_KEYS)
def test_verify_complete_rejects_invalid_key_before_hmac(monkeypatch, invalid_key):
    codec, complete = modules()
    raw = codec.encode_document(
        "complete", complete.create_complete(unsigned_complete(), KEY))
    monkeypatch.setattr(complete.hmac, "new", _forbid_hmac)
    with pytest.raises(complete.CompleteIntegrityError, match="invalid key"):
        complete.verify_complete(raw, invalid_key)


def test_complete_schema_requires_mac_field():
    jsonschema = pytest.importorskip("jsonschema")
    schema = __import__("json").loads(
        (ROOT / "schemas/legal-rule-complete.schema.json").read_text(encoding="utf-8"))
    document = {**unsigned_complete(), "complete_mac": "c" * 64}
    jsonschema.validate(document, schema)
    document.pop("complete_mac")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(document, schema)
