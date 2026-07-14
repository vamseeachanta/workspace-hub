from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))

from rule_authority import authority, codec  # noqa: E402


REV = "12345678-1234-4234-9234-123456789abc"
RULE = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def registry(generation=1):
    return {
        "authority_revision": REV,
        "generation": generation,
        "rules": [
            {
                "match_mode": "exact-bytes",
                "rule_id": RULE,
                "severity": "block",
                "target": "both",
            }
        ],
        "schema_id": "legal-rule-registry-v1",
    }


def policy(generation=1):
    return {
        "authority_revision": REV,
        "forensic_prefixes": ["docs/"],
        "generation": generation,
        "limits": {
            "max_blob_bytes": 1024,
            "max_entries": 100,
            "max_findings": 10,
            "max_request_bytes": 4096,
        },
        "schema_id": "legal-rule-policy-v1",
    }


def private_map(generation=1, pattern=b"synthetic-forbidden-value"):
    return {
        "authority_revision": REV,
        "generation": generation,
        "rules": [{"pattern_b64": base64.b64encode(pattern).decode(), "rule_id": RULE}],
        "schema_id": "legal-rule-map-v1",
    }


def canonical(value):
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
        + b"\n"
    )


def test_complete_codec_and_manifest_golden_vector():
    key = bytes(range(32))
    sealed = authority.build_manifest(registry(), policy(), private_map(), key)
    expected_input = (
        b"LEGAL-RULE-AUTHORITY\0v1\0" + (1).to_bytes(8, "big") + uuid.UUID(REV).bytes
    )
    expected_input += b"".join(
        hashlib.sha256(canonical(x)).digest()
        for x in (registry(), policy(), private_map())
    )
    assert (
        sealed["manifest_mac"]
        == hmac.new(key, expected_input, hashlib.sha256).hexdigest()
    )
    assert codec.parse_registry(canonical(registry())) == registry()
    assert codec.parse_policy(canonical(policy())) == policy()
    assert codec.parse_map(canonical(private_map()), registry()) == private_map()


@pytest.mark.parametrize(
    "payload",
    [
        b'\xef\xbb\xbf{"schema_id":"legal-rule-registry-v1"}\n',
        b'{"schema_id":"legal-rule-registry-v1","schema_id":"legal-rule-registry-v1"}\n',
        canonical({**registry(), "unknown": True}),
        canonical({**registry(), "authority_revision": "NOT-A-UUID"}),
    ],
)
def test_codec_rejects_hostile_inputs_without_echo(payload):
    with pytest.raises(codec.AuthorityError) as caught:
        codec.parse_registry(payload)
    assert "synthetic-forbidden-value" not in str(caught.value)


def test_map_rejects_noncanonical_base64_and_unknown_rule():
    bad = private_map()
    bad["rules"][0]["pattern_b64"] = "c3ludGhldGljLWZvcmJpZGRlbi12YWx1ZQ"
    with pytest.raises(codec.AuthorityError):
        codec.parse_map(canonical(bad), registry())


def test_map_rejects_total_decoded_patterns_over_16k():
    second_id = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    reg = registry()
    reg["rules"].append(
        {
            "match_mode": "exact-bytes",
            "rule_id": second_id,
            "severity": "block",
            "target": "content",
        }
    )
    mapped = private_map(pattern=b"a" * 9000)
    mapped["rules"].append(
        {"pattern_b64": base64.b64encode(b"b" * 9000).decode(), "rule_id": second_id}
    )
    with pytest.raises(codec.AuthorityError):
        codec.parse_map(canonical(mapped), reg)
    bad = private_map()
    bad["rules"][0]["rule_id"] = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    with pytest.raises(codec.AuthorityError):
        codec.parse_map(canonical(bad), registry())


def test_verify_rejects_rollback_revision_reuse_and_tamper():
    key = bytes(range(32))
    manifest = authority.build_manifest(registry(), policy(), private_map(), key)
    anchor = authority.make_anchor(manifest, "f" * 40)
    ledger = authority.new_ledger("synthetic-key", manifest, key)
    authority.verify_bundle(
        registry(), policy(), private_map(), manifest, key, anchor, ledger, "f" * 40
    )
    old = dict(anchor)
    old["generation"] = 2
    with pytest.raises(codec.AuthorityError, match="integrity"):
        authority.verify_bundle(
            registry(), policy(), private_map(), manifest, key, old, ledger, "f" * 40
        )
    tampered = private_map(pattern=b"different")
    with pytest.raises(codec.AuthorityError, match="integrity"):
        authority.verify_bundle(
            registry(), policy(), tampered, manifest, key, anchor, ledger, "f" * 40
        )


def test_verify_binds_ledger_tool_sha_and_pending_head():
    key = bytes(range(32))
    manifest = authority.build_manifest(registry(), policy(), private_map(), key)
    ledger = authority.new_ledger("synthetic-key", manifest, key)
    anchor = authority.make_anchor(
        manifest, "f" * 40, slot="pending", expected_head_oid="e" * 40
    )
    authority.verify_bundle(
        registry(),
        policy(),
        private_map(),
        manifest,
        key,
        anchor,
        ledger,
        "f" * 40,
        "e" * 40,
    )
    for tool, head in (("d" * 40, "e" * 40), ("f" * 40, "d" * 40)):
        with pytest.raises(codec.AuthorityError, match="integrity"):
            authority.verify_bundle(
                registry(),
                policy(),
                private_map(),
                manifest,
                key,
                anchor,
                ledger,
                tool,
                head,
            )


def test_structural_scan_rejects_secret_artifacts_under_arbitrary_names(tmp_path):
    key = bytes(range(32))
    manifest = authority.build_manifest(registry(), policy(), private_map(), key)
    artifacts = authority.structural_tokens(private_map(), manifest, key)
    target = tmp_path / "innocent.bin"
    target.write_bytes(b"prefix" + artifacts[0] + b"suffix")
    findings = authority.scan_paths([target], artifacts)
    assert findings == 1
    assert str(target) not in str(findings)


def test_generation_ledger_append_is_authenticated_and_monotonic():
    key = bytes(range(32))
    manifest = authority.build_manifest(registry(), policy(), private_map(), key)
    ledger = authority.new_ledger("synthetic-key", manifest, key)
    authority.verify_ledger(ledger, key)
    next_manifest = dict(manifest)
    next_manifest["generation"] = 2
    next_manifest["authority_revision"] = "87654321-4321-4321-8321-cba987654321"
    next_manifest["manifest_mac"] = "1" * 64
    appended = authority.append_ledger(ledger, next_manifest, key)
    authority.verify_ledger(appended, key)
    with pytest.raises(codec.AuthorityError, match="integrity"):
        authority.append_ledger(appended, next_manifest, key)
