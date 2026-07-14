"""Synthetic sealing and anti-rollback verification primitives."""

from __future__ import annotations

import hashlib
import hmac
import struct
import uuid

from .codec import canonical_bytes, decode_document

AUTHORITY_DOMAIN = b"LEGAL-RULE-AUTHORITY\0v1\0"
LEDGER_DOMAIN = b"LEGAL-RULE-GENERATION-LEDGER\0v1\0"


class AuthorityIntegrityError(ValueError):
    """Authenticated authority state is invalid or rolled back."""


def _digest(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def _mac_input(generation: int, revision: str, digests: tuple[bytes, bytes, bytes]) -> bytes:
    return (AUTHORITY_DOMAIN + struct.pack(">Q", generation) +
            uuid.UUID(revision).bytes + b"".join(digests))


def manifest_mac_input(registry: bytes, policy: bytes, private_map: bytes) -> bytes:
    """Return the frozen domain-separated MAC input for canonical documents."""
    documents = (
        decode_document("registry", registry),
        decode_document("policy", policy),
        decode_document("map", private_map),
    )
    generations = {doc["generation"] for doc in documents}
    revisions = {doc["authority_revision"] for doc in documents}
    if len(generations) != 1 or len(revisions) != 1:
        raise AuthorityIntegrityError("authority identity mismatch")
    digests = tuple(_digest(value) for value in (registry, policy, private_map))
    return _mac_input(generations.pop(), revisions.pop(), digests)


def create_manifest(registry: bytes, policy: bytes, private_map: bytes, key: bytes) -> dict:
    if len(key) != 32:
        raise AuthorityIntegrityError("invalid key")
    documents = (
        decode_document("registry", registry),
        decode_document("policy", policy),
        decode_document("map", private_map),
    )
    generations = {doc["generation"] for doc in documents}
    revisions = {doc["authority_revision"] for doc in documents}
    if len(generations) != 1 or len(revisions) != 1:
        raise AuthorityIntegrityError("authority identity mismatch")
    digests = tuple(_digest(value) for value in (registry, policy, private_map))
    mac = hmac.new(key, manifest_mac_input(registry, policy, private_map),
                   hashlib.sha256).hexdigest()
    return {
        "authority_revision": documents[0]["authority_revision"],
        "generation": documents[0]["generation"],
        "manifest_mac": mac,
        "map_sha256": digests[2].hex(),
        "policy_sha256": digests[1].hex(),
        "registry_sha256": digests[0].hex(),
        "schema_id": "legal-rule-authority-manifest-v1",
    }


def _ledger_mac(document: dict, key: bytes) -> str:
    unsigned = {name: value for name, value in document.items() if name != "ledger_mac"}
    return hmac.new(key, LEDGER_DOMAIN + canonical_bytes(unsigned), hashlib.sha256).hexdigest()


def create_ledger(key_id: str, entries: list[dict], key: bytes) -> dict:
    document = {
        "entries": entries,
        "key_id": key_id,
        "schema_id": "legal-rule-generation-ledger-v1",
    }
    document["ledger_mac"] = _ledger_mac(document, key)
    return document


def _verify_ledger(ledger: dict, key: bytes) -> None:
    expected = _ledger_mac(ledger, key)
    if not hmac.compare_digest(expected, ledger["ledger_mac"]):
        raise AuthorityIntegrityError("ledger authentication failed")


def append_ledger(ledger: dict, generation: int, revision: str,
                  manifest_mac: str, key: bytes) -> dict:
    _verify_ledger(ledger, key)
    entries = ledger["entries"]
    tip = entries[-1]
    if generation != tip["generation"] + 1:
        raise AuthorityIntegrityError("generation is not tip plus one")
    if revision in {entry["authority_revision"] for entry in entries}:
        raise AuthorityIntegrityError("authority revision reused")
    new_entry = {"authority_revision": revision, "generation": generation,
                 "manifest_mac": manifest_mac}
    return create_ledger(ledger["key_id"], [*entries, new_entry], key)


def _verify_anchor(anchor: dict, manifest: dict, ledger: dict) -> None:
    identity = ("authority_revision", "generation", "manifest_mac")
    if any(anchor[name] != manifest[name] for name in identity):
        raise AuthorityIntegrityError("active anchor mismatch")
    tip = ledger["entries"][-1]
    if any(tip[name] != manifest[name] for name in identity):
        raise AuthorityIntegrityError("ledger tip mismatch")


def verify_bundle(registry: bytes, policy: bytes, private_map: bytes,
                  manifest_bytes: bytes, anchor_bytes: bytes,
                  ledger_bytes: bytes, key: bytes) -> None:
    manifest = decode_document("manifest", manifest_bytes)
    anchor = decode_document("anchor", anchor_bytes)
    ledger = decode_document("ledger", ledger_bytes)
    _verify_ledger(ledger, key)
    expected = create_manifest(registry, policy, private_map, key)
    for name, value in expected.items():
        actual = manifest[name]
        if name == "manifest_mac":
            if not hmac.compare_digest(value, actual):
                raise AuthorityIntegrityError("manifest authentication failed")
        elif value != actual:
            raise AuthorityIntegrityError("manifest component mismatch")
    _verify_anchor(anchor, manifest, ledger)
