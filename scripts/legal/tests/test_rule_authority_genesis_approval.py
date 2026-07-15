"""RED contract tests for the private genesis approval parser (issue #3544).

The verifier module is intentionally not present in this TDD slice.  These
tests specify its public parser boundary without coupling to implementation
details or filesystem state.
"""

import json
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))

from importlib import import_module  # noqa: E402

verifier = import_module("verify_rule_authority_genesis_approval")


def canonical_record() -> dict:
    identity = {
        "path": "scripts/legal/manage_rule_authority.py",
        "blob_oid": "a" * 40,
        "sha256": "b" * 64,
    }
    return {
        "schema_id": "legal-rule-genesis-approval-v1",
        "git_object_format": "sha1",
        "plan_commit": "c" * 40,
        "tool_commit_a": "d" * 40,
        "caller_commit_b": "e" * 40,
        "post_merge_main": "f" * 40,
        "transaction_id": str(uuid.uuid4()),
        "contract": identity,
        "launcher": {**identity, "path": "scripts/legal/launch_rule_authority_genesis.sh"},
        "execution_manifest": {
            **identity,
            "path": "config/legal-rule-authority-genesis-execution-manifest.json",
        },
        "approval_verifier": {
            **identity,
            "path": "scripts/legal/verify_rule_authority_genesis_approval.py",
        },
        "outer_bootstrap": {"sha256": "1" * 64},
        "python": {"realpath": "/usr/bin/python3", "sha256": "2" * 64},
        "host": {
            "hostname": "ace-linux-1",
            "machine_id_sha256": "3" * 64,
            "ssh_host_key": {
                "path": "/etc/ssh/ssh_host_ed25519_key.pub",
                "key_type": "ssh-ed25519",
                "sha256_fingerprint": "SHA256:" + "A" * 43,
            },
            "account": {"name": "operator", "uid": 1000, "home": "/home/operator"},
            "output_parent": "/home/operator/.local/share/legal-rule-authority",
            "mount": {
                "mount_id": 42,
                "major_minor": "8:1",
                "root": "/",
                "mountpoint": "/",
                "filesystem_type": "ext4",
                "source": "/dev/sda1",
                "options": ["rw", "relatime"],
            },
        },
    }


def canonical_bytes(record: dict) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def test_parser_accepts_canonical_typed_record():
    parsed = verifier.parse_canonical_approval(canonical_bytes(canonical_record()))
    assert parsed == canonical_record()


@pytest.mark.parametrize(
    "mutator",
    [
        lambda r: r.update({"unexpected": 1}),
        lambda r: r["contract"].update({"extra": "x"}),
        lambda r: r.pop("host"),
        lambda r: r["host"]["account"].update({"uid": True}),
        lambda r: r.update({"transaction_id": "not-a-uuid"}),
        lambda r: r.update({"plan_commit": "A" * 40}),
        lambda r: r["outer_bootstrap"].update({"sha256": "bad"}),
    ],
)
def test_parser_rejects_schema_and_type_mutations(mutator):
    record = canonical_record()
    mutator(record)
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(canonical_bytes(record))


@pytest.mark.parametrize(
    "raw",
    [
        lambda b: b.replace(b"{", b"{" + b"\xef\xbb\xbf", 1),
        lambda b: b.replace(b"\n", b"\r\n"),
        lambda b: b.replace(b'"schema_id"', b'"schema_id","schema_id"', 1),
        lambda b: b + b"x" * 16385,
    ],
)
def test_parser_rejects_noncanonical_bytes(raw):
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(raw(canonical_bytes(canonical_record())))


def test_parser_rejects_noncanonical_whitespace_order_escaping_and_trailing_bytes():
    record = canonical_record()
    pretty = (json.dumps(record, sort_keys=False, indent=2) + "\n").encode()
    reordered = (json.dumps(record, sort_keys=False, separators=(",", ":")) + "\n").encode()
    escaped = canonical_bytes(record).replace(b"ace-linux-1", b"ace-\\u006cinux-1")
    for raw in (pretty, reordered, escaped, canonical_bytes(record) + b"\n", canonical_bytes(record)[:-1]):
        with pytest.raises(ValueError):
            verifier.parse_canonical_approval(raw)


@pytest.mark.parametrize(
    "field",
    ["launcher", "execution_manifest", "approval_verifier", "python", "host"],
)
def test_parser_enforces_exact_nested_key_sets(field):
    record = canonical_record()
    record[field]["unexpected"] = "x"
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(canonical_bytes(record))


@pytest.mark.parametrize("field", ["contract", "launcher", "execution_manifest", "approval_verifier"])
@pytest.mark.parametrize("leaf,value", [("blob_oid", "A" * 40), ("blob_oid", "a" * 39), ("sha256", "B" * 64), ("sha256", "b" * 63), ("path", 7)])
def test_parser_rejects_malformed_identity_leaves(field, leaf, value):
    record = canonical_record()
    record[field][leaf] = value
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(canonical_bytes(record))


@pytest.mark.parametrize(
    "path, value",
    [
        (("python", "realpath"), 7),
        (("python", "sha256"), "x" * 64),
        (("host", "hostname"), 7),
        (("host", "machine_id_sha256"), "x" * 64),
        (("host", "ssh_host_key", "key_type"), 7),
        (("host", "ssh_host_key", "sha256_fingerprint"), "SHA256:bad"),
        (("host", "account", "uid"), True),
        (("host", "account", "home"), "relative"),
        (("host", "mount", "mount_id"), True),
        (("host", "mount", "major_minor"), "bad"),
        (("host", "mount", "options"), "rw"),
    ],
)
def test_parser_rejects_malformed_python_and_host_facts(path, value):
    record = canonical_record()
    target = record
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(canonical_bytes(record))


@pytest.mark.parametrize(
    "path",
    [
        ("launcher", "path"),
        ("execution_manifest", "sha256"),
        ("approval_verifier", "blob_oid"),
        ("python", "realpath"),
        ("host", "ssh_host_key", "path"),
        ("host", "account", "name"),
        ("host", "mount", "filesystem_type"),
    ],
)
def test_parser_rejects_missing_nested_fields(path):
    record = canonical_record()
    target = record
    for part in path[:-1]:
        target = target[part]
    del target[path[-1]]
    with pytest.raises(ValueError):
        verifier.parse_canonical_approval(canonical_bytes(record))
