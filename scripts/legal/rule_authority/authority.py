"""Sealing, verification, anti-rollback, and structural-artifact primitives."""

from __future__ import annotations

import base64
import hashlib
import hmac
import uuid
from pathlib import Path

from . import codec


DOMAIN = b"LEGAL-RULE-AUTHORITY\0v1\0"
LEDGER_DOMAIN = b"LEGAL-RULE-LEDGER\0v1\0"


def _sha(value):
    return hashlib.sha256(codec.canonical_bytes(value)).digest()


def _mac_input(registry, policy, private_map):
    generation = registry["generation"].to_bytes(8, "big")
    revision = uuid.UUID(registry["authority_revision"]).bytes
    return (
        DOMAIN
        + generation
        + revision
        + _sha(registry)
        + _sha(policy)
        + _sha(private_map)
    )


def build_manifest(registry, policy, private_map, key):
    codec.parse_registry(codec.canonical_bytes(registry))
    codec.parse_policy(codec.canonical_bytes(policy))
    codec.parse_map(codec.canonical_bytes(private_map), registry)
    if len(key) != 32 or (policy["generation"], policy["authority_revision"]) != (
        registry["generation"],
        registry["authority_revision"],
    ):
        raise codec.AuthorityError("schema")
    return {
        "authority_revision": registry["authority_revision"],
        "generation": registry["generation"],
        "manifest_mac": hmac.new(
            key, _mac_input(registry, policy, private_map), hashlib.sha256
        ).hexdigest(),
        "map_sha256": _sha(private_map).hex(),
        "policy_sha256": _sha(policy).hex(),
        "registry_sha256": _sha(registry).hex(),
        "schema_id": "legal-rule-authority-manifest-v1",
    }


def make_anchor(manifest, tool_sha, slot="current", expected_head_oid=None):
    return {
        "authority_revision": manifest["authority_revision"],
        "generation": manifest["generation"],
        "manifest_mac": manifest["manifest_mac"],
        "schema_id": "legal-rule-active-anchor-v1",
        "slot": slot,
        "tool_sha": tool_sha,
        "expected_head_oid": expected_head_oid,
    }


def verify_bundle(
    registry,
    policy,
    private_map,
    manifest,
    key,
    anchor,
    ledger,
    tool_sha,
    head_oid=None,
):
    expected = build_manifest(registry, policy, private_map, key)
    identity = ("authority_revision", "generation", "manifest_mac")
    verify_ledger(ledger, key)
    tip = ledger["entries"][-1]
    invalid = not hmac.compare_digest(
        codec.canonical_bytes(expected), codec.canonical_bytes(manifest)
    )
    invalid |= any(anchor.get(k) != manifest.get(k) for k in identity)
    invalid |= any(tip.get(k) != manifest.get(k) for k in identity)
    invalid |= anchor.get("tool_sha") != tool_sha
    invalid |= (
        anchor.get("slot") == "pending" and anchor.get("expected_head_oid") != head_oid
    )
    if invalid:
        raise codec.AuthorityError("integrity")
    codec.parse_anchor(codec.canonical_bytes(anchor))
    return True


def _ledger_mac(value, key):
    bare = {k: v for k, v in value.items() if k != "ledger_mac"}
    return hmac.new(
        key, LEDGER_DOMAIN + codec.canonical_bytes(bare), hashlib.sha256
    ).hexdigest()


def new_ledger(key_id, manifest, key):
    value = {
        "entries": [
            {
                k: manifest[k]
                for k in ("generation", "authority_revision", "manifest_mac")
            }
        ],
        "key_id": key_id,
        "schema_id": "legal-rule-generation-ledger-v1",
    }
    return {**value, "ledger_mac": _ledger_mac(value, key)}


def verify_ledger(ledger, key):
    codec.parse_ledger(codec.canonical_bytes(ledger))
    if (
        set(ledger) != {"entries", "key_id", "schema_id", "ledger_mac"}
        or ledger["schema_id"] != "legal-rule-generation-ledger-v1"
    ):
        raise codec.AuthorityError("integrity")
    if not hmac.compare_digest(ledger["ledger_mac"], _ledger_mac(ledger, key)):
        raise codec.AuthorityError("integrity")
    generations = [x["generation"] for x in ledger["entries"]]
    revisions = [x["authority_revision"] for x in ledger["entries"]]
    if generations != list(
        range(generations[0], generations[0] + len(generations))
    ) or len(revisions) != len(set(revisions)):
        raise codec.AuthorityError("integrity")
    return True


def append_ledger(ledger, manifest, key):
    verify_ledger(ledger, key)
    entries = list(ledger["entries"])
    tip = entries[-1]
    if manifest["generation"] != tip["generation"] + 1 or manifest[
        "authority_revision"
    ] in {x["authority_revision"] for x in entries}:
        raise codec.AuthorityError("integrity")
    entries.append(
        {k: manifest[k] for k in ("generation", "authority_revision", "manifest_mac")}
    )
    bare = {
        "entries": entries,
        "key_id": ledger["key_id"],
        "schema_id": ledger["schema_id"],
    }
    return {**bare, "ledger_mac": _ledger_mac(bare, key)}


def structural_tokens(private_map, manifest, key, anchor=None, ledger=None):
    patterns = [base64.b64decode(x["pattern_b64"]) for x in private_map["rules"]]
    tokens = [
        codec.canonical_bytes(private_map),
        codec.canonical_bytes(manifest),
        key,
        base64.b64encode(key),
        b"legal-rule-map-v1",
        b"legal-rule-authority-manifest-v1",
        b"legal-rule-active-anchor-v1",
        b"legal-rule-generation-ledger-v1",
        b"legal-rule-complete-v1",
    ]
    artifacts = [value for value in (anchor, ledger) if value]
    tokens.extend(codec.canonical_bytes(value) for value in artifacts)
    for value in (manifest, *artifacts):
        tokens.extend(
            str(item).encode("ascii")
            for item in value.values()
            if isinstance(item, (str, int))
        )
    tokens.extend(
        [
            b"PACK",
            b"\xfftOc",
            b"repositoryformatversion",
            b"legal-rule-private-report-v1",
        ]
    )
    return tokens + patterns + [base64.b64encode(value) for value in patterns]


def scan_paths(paths, tokens):
    findings = 0
    for path in paths:
        data = Path(path).read_bytes()
        if any(token and token in data for token in tokens):
            findings += 1
    return findings
