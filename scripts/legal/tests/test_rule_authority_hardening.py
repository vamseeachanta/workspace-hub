"""Adversarial cross-document and structural authority tests."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import base64
import hashlib
import importlib
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, POLICY, PRIVATE_MAP, REGISTRY

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
sys.path.insert(0, str(LEGAL))


def module(name: str):
    return importlib.import_module(f"rule_authority.{name}")


def encoded_documents(registry=REGISTRY, private_map=PRIVATE_MAP):
    codec = module("codec")
    return (
        codec.encode_document("registry", registry),
        codec.encode_document("policy", POLICY),
        codec.encode_document("map", private_map),
    )


@pytest.mark.parametrize("change", ["missing", "extra", "different"])
def test_registry_map_rule_ids_require_exact_parity(change):
    seal = module("seal")
    private_map = deepcopy(PRIVATE_MAP)
    other_id = "423e4567-e89b-42d3-a456-426614174000"
    if change == "missing":
        registry = deepcopy(REGISTRY)
        registry["rules"].append(dict(registry["rules"][0], rule_id=other_id))
        registry["rules"].sort(key=lambda item: item["rule_id"])
    elif change == "extra":
        registry = REGISTRY
        private_map["rules"].append({"pattern_b64": "ZXh0cmE=", "rule_id": other_id})
        private_map["rules"].sort(key=lambda item: item["rule_id"])
    else:
        registry = REGISTRY
        private_map["rules"][0]["rule_id"] = other_id
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.create_manifest(*encoded_documents(registry, private_map), KEY)


def test_ascii_fold_pattern_requires_ascii_bytes():
    seal = module("seal")
    registry = deepcopy(REGISTRY)
    registry["rules"][0]["match_mode"] = "ascii-fold"
    private_map = deepcopy(PRIVATE_MAP)
    private_map["rules"][0]["pattern_b64"] = base64.b64encode(b"bad-\xff").decode()
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.create_manifest(*encoded_documents(registry, private_map), KEY)


def _valid_state():
    seal = module("seal")
    codec = module("codec")
    registry, policy, private_map = encoded_documents()
    manifest = seal.create_manifest(registry, policy, private_map, KEY)
    entry = {"authority_revision": manifest["authority_revision"],
             "generation": manifest["generation"],
             "manifest_mac": manifest["manifest_mac"]}
    ledger = seal.create_ledger("synthetic-key", [entry], KEY)
    anchor = {**entry, "expected_head_oid": None,
              "schema_id": "legal-rule-active-anchor-v1", "slot": "current",
              "tool_sha": "a" * 40}
    return registry, policy, private_map, *(codec.encode_document(kind, value) for kind, value in (
        ("manifest", manifest), ("anchor", anchor), ("ledger", ledger)))


def test_anchor_identity_is_authenticated_before_map_decode(monkeypatch):
    seal = module("seal")
    codec = module("codec")
    registry, policy, private_map, manifest, anchor, ledger = _valid_state()
    anchor_doc = codec.decode_document("anchor", anchor)
    anchor_doc["generation"] -= 1
    stale_anchor = codec.encode_document("anchor", anchor_doc)
    decoded_kinds = []
    real_decode = seal.decode_document

    def observed(kind, raw):
        decoded_kinds.append(kind)
        return real_decode(kind, raw)

    monkeypatch.setattr(seal, "decode_document", observed)
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.verify_bundle(registry, policy, private_map, manifest, stale_anchor, ledger, KEY)
    assert "map" not in decoded_kinds


def test_ledger_tamper_and_non_tip_anchor_reject():
    seal = module("seal")
    codec = module("codec")
    registry, policy, private_map, manifest, anchor, ledger = _valid_state()
    ledger_doc = codec.decode_document("ledger", ledger)
    ledger_doc["ledger_mac"] = "0" * 64
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.verify_bundle(registry, policy, private_map, manifest, anchor,
                           codec.encode_document("ledger", ledger_doc), KEY)


def test_structural_inventory_covers_raw_hashes_values_and_markers():
    structural = module("structural")
    pattern = b"synthetic-block-token"
    artifact = b'{"private":"report"}\n'
    digest = hashlib.sha256(artifact).digest()
    sensitive = structural.SensitiveArtifacts(
        key=KEY,
        decoded_patterns=(pattern,),
        exact_artifacts=(artifact,),
        prohibited_basenames=frozenset({"authority.bundle"}),
        digests=(digest,),
        individual_values=(b"synthetic-snapshot-id",),
    )
    payloads = (
        pattern,
        digest,
        digest.hex().encode(),
        b"legal-rule-private-report-v1",
        b"legal-rule-coverage-v1",
        b"core.repositoryformatversion",
        b"synthetic-snapshot-id",
    )
    for index, payload in enumerate(payloads):
        path = f"arbitrary/{index}.bin"
        assert structural.scan_blobs({path: b"x" + payload + b"y"}, sensitive) == [path]
    assert structural.scan_blobs({"x/authority.bundle": b"innocent"}, sensitive)


def test_structural_scanner_does_not_block_canonical_public_artifacts():
    structural = module("structural")
    sensitive = structural.SensitiveArtifacts(KEY, (), (), frozenset())
    schema_names = (
        "registry", "policy", "map", "authority-manifest", "active-anchor",
        "generation-ledger", "complete",
    )
    paths = tuple(f"schemas/legal-rule-{name}.schema.json" for name in schema_names) + (
        "config/legal-rule-registry.json",
        "config/legal-rule-authority-policy.json",
    )
    blobs = {path: (ROOT / path).read_bytes() for path in paths if (ROOT / path).exists()}
    assert structural.scan_blobs(blobs, sensitive) == []


@pytest.mark.parametrize("generation", [-1, 0, True, 2.0, 1 << 64])
def test_generation_hostile_values_reject(generation):
    codec = module("codec")
    document = deepcopy(REGISTRY)
    document["generation"] = generation
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("registry", document)


@pytest.mark.parametrize("revision", [
    "123E4567-E89B-42D3-A456-426614174000",
    "123e4567-e89b-12d3-a456-426614174000",
    "not-a-uuid",
])
def test_revision_requires_canonical_lowercase_uuid4(revision):
    codec = module("codec")
    document = deepcopy(REGISTRY)
    document["authority_revision"] = revision
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("registry", document)


def test_document_size_order_and_path_traversal_reject():
    codec = module("codec")
    oversized = deepcopy(PRIVATE_MAP)
    oversized["rules"][0]["pattern_b64"] = base64.b64encode(b"x" * 16_385).decode()
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("map", oversized)
    policy = deepcopy(POLICY)
    policy["forensic_prefixes"] = ["z/", "a/"]
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("policy", policy)
    policy["forensic_prefixes"] = ["safe/../escape/"]
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("policy", policy)


@pytest.mark.parametrize("key_id", ["bad\nkey", "x" * 129])
def test_ledger_rejects_generation_gaps_and_hostile_key_ids(key_id):
    codec = module("codec")
    ledger = {
        "entries": [
            {"authority_revision": "223e4567-e89b-42d3-a456-426614174000",
             "generation": 1, "manifest_mac": "a" * 64},
            {"authority_revision": "423e4567-e89b-42d3-a456-426614174000",
             "generation": 3, "manifest_mac": "b" * 64},
        ],
        "key_id": key_id,
        "ledger_mac": "c" * 64,
        "schema_id": "legal-rule-generation-ledger-v1",
    }
    with pytest.raises(codec.AuthorityFormatError):
        codec.encode_document("ledger", ledger)


def test_parser_and_integrity_errors_withhold_hostile_bytes():
    codec = module("codec")
    hostile = "sensitive-synthetic-fragment"
    raw = ('{"schema_id":"' + hostile + '"}\n').encode()
    with pytest.raises(codec.AuthorityFormatError) as caught:
        codec.decode_document("registry", raw)
    assert hostile not in str(caught.value)
