"""Contract tests for canonical public/private authority documents."""

from __future__ import annotations

import importlib
import hashlib
import math
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import POLICY, PRIVATE_MAP, REGISTRY, changed

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
PACKAGE = LEGAL / "rule_authority"


def load_module(name: str):
    """Load a module only after asserting the wished-for production path."""
    path = PACKAGE / f"{name}.py"
    assert path.is_file(), f"missing Phase A module: {path.relative_to(ROOT)}"
    sys.path.insert(0, str(LEGAL))
    return importlib.import_module(f"rule_authority.{name}")


def test_complete_codec_golden_vectors():
    codec = load_module("codec")
    expected = {
        "registry": (
        b'{"authority_revision":"123e4567-e89b-42d3-a456-426614174000",'
        b'"generation":2,"rules":[{"match_mode":"exact-bytes",'
        b'"rule_id":"323e4567-e89b-42d3-a456-426614174000",'
        b'"severity":"block","target":"both"}],'
        b'"schema_id":"legal-rule-registry-v1"}\n'
        ),
        "policy": (
        b'{"authority_revision":"123e4567-e89b-42d3-a456-426614174000",'
        b'"forensic_prefixes":["docs/forensic/"],"generation":2,"limits":'
        b'{"max_blob_bytes":1024,"max_entries":100,"max_findings":10,'
        b'"max_request_bytes":4096},"schema_id":"legal-rule-policy-v1"}\n'
        ),
        "map": (
        b'{"authority_revision":"123e4567-e89b-42d3-a456-426614174000",'
        b'"generation":2,"rules":[{"pattern_b64":"c3ludGhldGljLWJsb2NrLXRva2Vu",'
        b'"rule_id":"323e4567-e89b-42d3-a456-426614174000"}],'
        b'"schema_id":"legal-rule-map-v1"}\n'
        ),
    }
    documents = {"registry": REGISTRY, "policy": POLICY, "map": PRIVATE_MAP}
    digests = {
        "registry": "5c16c8b6935afd495bda79961d717cb8e4460dd5dc51558f0595a3269581b835",
        "policy": "3e8496ae400736a9819f745267dbdc65fae48623e293eaf9aeba939b94b92b56",
        "map": "709cd63a7e5f5296e84e623f4780a3e56a1eff92ebd9f5593ecebb3f246112cc",
    }
    for kind, raw in expected.items():
        assert codec.encode_document(kind, documents[kind]) == raw
        assert codec.decode_document(kind, raw) == documents[kind]
        assert hashlib.sha256(raw).hexdigest() == digests[kind]


@pytest.mark.parametrize(
    ("kind", "document"),
    [("registry", REGISTRY), ("policy", POLICY), ("map", PRIVATE_MAP)],
)
def test_codec_round_trip_is_exact(kind, document):
    codec = load_module("codec")
    encoded = codec.encode_document(kind, document)
    assert encoded.endswith(b"\n")
    assert codec.encode_document(kind, codec.decode_document(kind, encoded)) == encoded


@pytest.mark.parametrize(
    "raw",
    [
        b'{"schema_id":"legal-rule-registry-v1","schema_id":"x"}\n',
        b'{}\ntrailing',
        b'\xef\xbb\xbf{}\n',
        b'{"generation":NaN}\n',
        b'\xff\n',
    ],
)
def test_codec_rejects_noncanonical_or_hostile_json(raw):
    codec = load_module("codec")
    with pytest.raises(codec.AuthorityFormatError):
        codec.decode_document("registry", raw)


def test_codec_rejects_unknown_keys_and_noncanonical_ordering():
    codec = load_module("codec")
    unknown = changed(REGISTRY, label="must-not-exist")
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("registry", unknown)
    reversed_rules = changed(REGISTRY, rules=[
        dict(REGISTRY["rules"][0], rule_id="423e4567-e89b-42d3-a456-426614174000"),
        REGISTRY["rules"][0],
    ])
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("registry", reversed_rules)


def test_codec_rejects_bool_float_and_noncanonical_base64():
    codec = load_module("codec")
    for generation in (True, 2.0, math.inf):
        with pytest.raises(codec.AuthorityFormatError):
            codec.encode_document("registry", changed(REGISTRY, generation=generation))
    bad_map = changed(PRIVATE_MAP)
    bad_map["rules"][0]["pattern_b64"] = "c3ludGhldGljLWJsb2NrLXRva2Vu="
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("map", bad_map)


def test_authority_schemas_exist_and_forbid_additional_properties():
    jsonschema = pytest.importorskip("jsonschema")
    for name, document in (("registry", REGISTRY), ("policy", POLICY), ("map", PRIVATE_MAP)):
        path = ROOT / "schemas" / f"legal-rule-{name}.schema.json"
        assert path.is_file(), f"missing schema: {path.relative_to(ROOT)}"
        schema = __import__("json").loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(document, schema)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(changed(document, unexpected="rejected"), schema)
