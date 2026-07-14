"""Synthetic MAC, anchor, ledger, and rollback contract tests."""

from __future__ import annotations

import importlib
import hashlib
import sys
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, OLD_REVISION, POLICY, PRIVATE_MAP, REGISTRY, REVISION

LEGAL = Path(__file__).resolve().parents[1]
ROOT = LEGAL.parents[1]
PACKAGE = LEGAL / "rule_authority"


def load_module(name: str):
    path = PACKAGE / f"{name}.py"
    assert path.is_file(), f"missing Phase A module: {path.relative_to(ROOT)}"
    sys.path.insert(0, str(LEGAL))
    return importlib.import_module(f"rule_authority.{name}")


def documents():
    codec = load_module("codec")
    return tuple(codec.encode_document(kind, doc) for kind, doc in (
        ("registry", REGISTRY), ("policy", POLICY), ("map", PRIVATE_MAP)
    ))


def test_manifest_mac_golden_vector():
    seal = load_module("seal")
    registry, policy, private_map = documents()
    manifest = seal.create_manifest(registry, policy, private_map, KEY)
    assert manifest == {
        "authority_revision": REVISION,
        "generation": 2,
        "manifest_mac": "baabf0644dd201d64265a731151c936ff7492642410719a14f30c93be21836d7",
        "map_sha256": "709cd63a7e5f5296e84e623f4780a3e56a1eff92ebd9f5593ecebb3f246112cc",
        "policy_sha256": "3e8496ae400736a9819f745267dbdc65fae48623e293eaf9aeba939b94b92b56",
        "registry_sha256": "5c16c8b6935afd495bda79961d717cb8e4460dd5dc51558f0595a3269581b835",
        "schema_id": "legal-rule-authority-manifest-v1",
    }


def test_manifest_mac_input_and_document_bytes_are_frozen():
    seal = load_module("seal")
    codec = load_module("codec")
    registry, policy, private_map = documents()
    manifest = seal.create_manifest(registry, policy, private_map, KEY)
    expected_input = (
        "4c4547414c2d52554c452d415554484f52495459007631000000000000000002"
        "123e4567e89b42d3a456426614174000"
        "5c16c8b6935afd495bda79961d717cb8e4460dd5dc51558f0595a3269581b835"
        "3e8496ae400736a9819f745267dbdc65fae48623e293eaf9aeba939b94b92b56"
        "709cd63a7e5f5296e84e623f4780a3e56a1eff92ebd9f5593ecebb3f246112cc"
    )
    assert seal.manifest_mac_input(registry, policy, private_map).hex() == expected_input
    raw = codec.encode_document("manifest", manifest)
    assert hashlib.sha256(raw).hexdigest() == "75a644212868aa3a08f9b9a4633cb18268e6ba8a1bbee3cdf16c78d202255734"
    assert raw.startswith(b'{"authority_revision":"123e4567-e89b-42d3-a456-426614174000"')
    assert raw.endswith(b'"schema_id":"legal-rule-authority-manifest-v1"}\n')


def test_valid_bundle_rejects_older_valid_replay_against_new_authority():
    seal = load_module("seal")
    codec = load_module("codec")
    registry, policy, private_map = documents()
    manifest = seal.create_manifest(registry, policy, private_map, KEY)
    manifest_bytes = codec.encode_document("manifest", manifest)
    old_documents = []
    for kind, document in (("registry", REGISTRY), ("policy", POLICY), ("map", PRIVATE_MAP)):
        old = dict(document, generation=1, authority_revision=OLD_REVISION)
        old_documents.append(codec.encode_document(kind, old))
    old_manifest = seal.create_manifest(*old_documents, KEY)
    genesis = seal.create_ledger("synthetic-key", [{"generation": 1,
        "authority_revision": OLD_REVISION, "manifest_mac": old_manifest["manifest_mac"]}], KEY)
    ledger = seal.append_ledger(genesis, 2, REVISION, manifest["manifest_mac"], KEY)
    anchor = {
        "authority_revision": REVISION,
        "expected_head_oid": None,
        "generation": 2,
        "manifest_mac": manifest["manifest_mac"],
        "schema_id": "legal-rule-active-anchor-v1",
        "slot": "current",
        "tool_sha": "a" * 40,
    }
    anchor_bytes = codec.encode_document("anchor", anchor)
    ledger_bytes = codec.encode_document("ledger", ledger)
    seal.verify_bundle(registry, policy, private_map, manifest_bytes, anchor_bytes, ledger_bytes, KEY)
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.verify_bundle(*old_documents, codec.encode_document("manifest", old_manifest),
                           anchor_bytes, ledger_bytes, KEY)


def test_anchor_and_ledger_genesis_append_bytes_are_frozen():
    seal = load_module("seal")
    codec = load_module("codec")
    registry, policy, private_map = documents()
    manifest = seal.create_manifest(registry, policy, private_map, KEY)
    anchor = {"authority_revision": REVISION, "expected_head_oid": None,
              "generation": 2, "manifest_mac": manifest["manifest_mac"],
              "schema_id": "legal-rule-active-anchor-v1", "slot": "current",
              "tool_sha": "a" * 40}
    old = {"authority_revision": OLD_REVISION, "generation": 1, "manifest_mac": "1" * 64}
    genesis = seal.create_ledger("synthetic-key", [old], KEY)
    appended = seal.append_ledger(genesis, 2, REVISION, manifest["manifest_mac"], KEY)
    assert hashlib.sha256(codec.encode_document("anchor", anchor)).hexdigest() == (
        "1756a2dfe35b1185fc5b932c2a19b2661e06f264c90f914622f636923176afec")
    assert genesis["ledger_mac"] == "7243a17796aec6277db1909f078c9366710c109d1e0b2dae6e8b1429791ce05e"
    assert appended["ledger_mac"] == "322c0abf80b69834122b2690b673a842dc4d096d873ac367a6481adbeace7e43"
    assert hashlib.sha256(codec.encode_document("ledger", genesis)).hexdigest() == (
        "efc0f83054f7552e29b10962e45deb5bcd6feaf0d24c6cd809cf9a35be506a44")
    assert hashlib.sha256(codec.encode_document("ledger", appended)).hexdigest() == (
        "3b412ce96dd0abffe051cc33bf01f7156ce47115edd9f22bffb5f64d873b921d")


def test_revision_reuse_and_nonsequential_append_reject():
    seal = load_module("seal")
    entry = {"generation": 2, "authority_revision": REVISION, "manifest_mac": "a" * 64}
    ledger = seal.create_ledger("synthetic-key", [entry], KEY)
    for generation, revision in ((2, "423e4567-e89b-42d3-a456-426614174000"), (3, REVISION), (4, "423e4567-e89b-42d3-a456-426614174000")):
        with pytest.raises(seal.AuthorityIntegrityError):
            seal.append_ledger(ledger, generation, revision, "b" * 64, KEY)


def test_manifest_anchor_and_ledger_schemas_exist():
    for name in ("authority-manifest", "active-anchor", "generation-ledger", "complete"):
        assert (ROOT / "schemas" / f"legal-rule-{name}.schema.json").is_file()
