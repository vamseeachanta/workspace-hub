"""Fresh RED tests for the second Phase-A1 correction slice."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from rule_authority_fixtures import KEY, OLD_REVISION, POLICY, PRIVATE_MAP, REGISTRY, REVISION

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))
LEDGER_DOMAIN = b"LEGAL-RULE-GENERATION-LEDGER\0v1\0"


def module(name: str):
    return importlib.import_module(f"rule_authority.{name}")


def canonical(value: object) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return (text + "\n").encode("ascii")


def signed_ledger(entries: list[dict], key_id: str = "synthetic-key") -> dict:
    unsigned = {"entries": entries, "key_id": key_id,
                "schema_id": "legal-rule-generation-ledger-v1"}
    digest = hmac.new(KEY, LEDGER_DOMAIN + canonical(unsigned), hashlib.sha256).hexdigest()
    return {**unsigned, "ledger_mac": digest}


def valid_entry() -> dict:
    return {"authority_revision": OLD_REVISION, "generation": 1,
            "manifest_mac": "1" * 64}


def valid_bundle():
    seal = module("seal")
    codec = module("codec")
    documents = tuple(codec.encode_document(kind, value) for kind, value in (
        ("registry", REGISTRY), ("policy", POLICY), ("map", PRIVATE_MAP)))
    manifest = seal.create_manifest(*documents, KEY)
    entry = {"authority_revision": REVISION, "generation": 2,
             "manifest_mac": manifest["manifest_mac"]}
    anchor = {**entry, "expected_head_oid": None,
              "schema_id": "legal-rule-active-anchor-v1", "slot": "current",
              "tool_sha": "a" * 40}
    ledger = signed_ledger([entry])
    encoded = tuple(codec.encode_document(kind, value) for kind, value in (
        ("manifest", manifest), ("anchor", anchor), ("ledger", ledger)))
    return (*documents, *encoded)


@pytest.mark.parametrize("bad_key", [b"x", b"x" * 31, b"x" * 33])
@pytest.mark.parametrize("operation", ["create", "append", "verify"])
def test_hmac_apis_reject_non_32_byte_keys_before_hmac(monkeypatch, bad_key, operation):
    seal = module("seal")
    ledger = signed_ledger([valid_entry()])
    bundle = valid_bundle()

    def forbidden_hmac(*_args, **_kwargs):
        raise AssertionError("HMAC ran before key validation")

    monkeypatch.setattr(seal.hmac, "new", forbidden_hmac)
    with pytest.raises(seal.AuthorityIntegrityError):
        if operation == "create":
            seal.create_ledger("synthetic-key", [valid_entry()], bad_key)
        elif operation == "append":
            seal.append_ledger(ledger, 2, REVISION, "2" * 64, bad_key)
        else:
            seal.verify_bundle(*bundle, bad_key)


def invalid_existing_entries() -> list[list[dict]]:
    first = valid_entry()
    second = {"authority_revision": REVISION, "generation": 2,
              "manifest_mac": "2" * 64}
    variants = [
        [{**first, "generation": 0}],
        [{**first, "authority_revision": "not-a-uuid"}],
        [{**first, "manifest_mac": "z" * 64}],
        [{**first, "unexpected": "field"}],
        [first, {**second, "generation": 3}],
        [first, {**second, "authority_revision": OLD_REVISION}],
    ]
    return variants


@pytest.mark.parametrize("entries", invalid_existing_entries())
def test_create_ledger_rejects_invalid_semantics(entries):
    seal = module("seal")
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.create_ledger("synthetic-key", entries, KEY)


@pytest.mark.parametrize("key_id", ["", "bad\nkey", "x" * 129])
def test_create_ledger_rejects_invalid_key_id(key_id):
    seal = module("seal")
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.create_ledger(key_id, [valid_entry()], KEY)


@pytest.mark.parametrize("entries", invalid_existing_entries())
def test_append_rejects_authenticated_but_invalid_existing_ledger(entries):
    seal = module("seal")
    ledger = signed_ledger(entries)
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.append_ledger(ledger, 4, REVISION, "2" * 64, KEY)


@pytest.mark.parametrize(("generation", "revision", "manifest_mac"), [
    (1 << 64, REVISION, "2" * 64),
    (2, "not-a-uuid", "2" * 64),
    (2, REVISION, "z" * 64),
])
def test_append_validates_completed_entry(generation, revision, manifest_mac):
    seal = module("seal")
    with pytest.raises(seal.AuthorityIntegrityError):
        seal.append_ledger(signed_ledger([valid_entry()]), generation, revision,
                           manifest_mac, KEY)


def test_append_does_not_mutate_caller_ledger():
    seal = module("seal")
    ledger = signed_ledger([valid_entry()])
    before = deepcopy(ledger)
    seal.append_ledger(ledger, 2, REVISION, "2" * 64, KEY)
    assert ledger == before
