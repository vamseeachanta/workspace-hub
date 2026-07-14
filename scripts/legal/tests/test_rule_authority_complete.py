"""Authenticated COMPLETE transaction codec vectors."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, REVISION

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
sys.path.insert(0, str(LEGAL))

COMPLETE_DOMAIN = b"LEGAL-RULE-COMPLETE\0v1\0"


def modules():
    return (importlib.import_module("rule_authority.codec"),
            importlib.import_module("rule_authority.complete"))


def unsigned_complete():
    return {
        "api_snapshot_id": "api-snapshot-synthetic",
        "authority_revision": REVISION,
        "coverage_states": {"git": "scanned"},
        "files": [{"path": "coverage.json", "sha256": "a" * 64, "size": 42}],
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
    assert document["complete_mac"] == expected_mac
    raw = codec.encode_document("complete", document)
    assert codec.decode_document("complete", raw) == document
    assert raw == codec.canonical_bytes(document)
    assert complete.verify_complete(raw, KEY) == document


def test_complete_tamper_and_key_size_reject():
    codec, complete = modules()
    document = complete.create_complete(unsigned_complete(), KEY)
    document["files"][0]["size"] += 1
    with pytest.raises(complete.CompleteIntegrityError):
        complete.verify_complete(codec.encode_document("complete", document), KEY)
    with pytest.raises(complete.CompleteIntegrityError):
        complete.create_complete(unsigned_complete(), KEY[:-1])


def test_complete_schema_requires_mac_field():
    jsonschema = pytest.importorskip("jsonschema")
    schema = __import__("json").loads(
        (ROOT / "schemas/legal-rule-complete.schema.json").read_text(encoding="utf-8"))
    document = {**unsigned_complete(), "complete_mac": "c" * 64}
    jsonschema.validate(document, schema)
    document.pop("complete_mac")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(document, schema)
