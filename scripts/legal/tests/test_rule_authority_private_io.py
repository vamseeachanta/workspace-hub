from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, envelope, private_io  # noqa: E402


IDENTITY = {
    "authority_revision": "12345678-1234-4234-9234-123456789abc",
    "generation": 1,
    "manifest_mac": "a" * 64,
}
TX = "12345678-1234-4234-9234-123456789abc"
KEY = b"k" * 32


def test_complete_binds_coverage_snapshots_and_verifies_exact_files(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    result = private_io.write_complete_transaction(
        parent,
        TX,
        {"report.json": b"{}\n"},
        KEY,
        IDENTITY,
        coverage={"git": "scanned", "github": "unknown-residual"},
        snapshots={"refs_before": "b" * 64, "refs_after": "b" * 64},
    )
    complete = private_io.verify_complete_transaction(result, KEY)
    assert complete["coverage"]["github"] == "unknown-residual"
    assert complete["snapshots"]["refs_before"] == "b" * 64
    (result / "extra").write_bytes(b"unexpected")
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.verify_complete_transaction(result, KEY)


def test_complete_verification_rejects_changed_file_and_mac(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    result = private_io.write_complete_transaction(
        parent, TX, {"report.json": b"{}\n"}, KEY, IDENTITY
    )
    (result / "report.json").write_bytes(b"changed\n")
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.verify_complete_transaction(result, KEY)

    second = private_io.write_complete_transaction(
        parent,
        "87654321-4321-4321-8321-cba987654321",
        {"report.json": b"{}\n"},
        KEY,
        IDENTITY,
    )
    raw = json.loads((second / "COMPLETE").read_text())
    raw["manifest_mac"] = "0" * 64
    (second / "COMPLETE").write_text(json.dumps(raw, separators=(",", ":")) + "\n")
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.verify_complete_transaction(second, KEY)


@pytest.mark.skipif(os.name == "nt", reason="POSIX ownership/mode contract")
def test_private_parent_and_files_must_be_private(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o755)
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.write_complete_transaction(
            parent, TX, {"report.json": b"{}\n"}, KEY, IDENTITY
        )


def test_envelope_materialization_is_no_overwrite_and_maps_filesystem(tmp_path):
    encoded = __import__("base64").b64encode(b"{}\n").decode()
    key = __import__("base64").b64encode(b"k" * 32 + b"\n").decode()
    payload = codec.canonical_bytes(
        {
            "anchor": encoded,
            "key": key,
            "ledger": encoded,
            "manifest": encoded,
            "map": encoded,
            "schema_id": "legal-rule-ci-envelope-v1",
        }
    )
    missing = tmp_path / "missing"
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        envelope.materialize(payload, missing)
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    envelope.materialize(payload, private)
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        envelope.materialize(payload, private)
    if os.name != "nt":
        assert all((path.stat().st_mode & 0o077) == 0 for path in private.iterdir())


def test_private_child_directory_is_created_no_overwrite_through_stable_handle(
    tmp_path,
):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    with private_io.create_private_child(parent, "mirror.git") as (stable, pass_fds):
        assert Path(stable).is_dir()
        assert pass_fds == () if os.name == "nt" else len(pass_fds) == 2
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        with private_io.create_private_child(parent, "mirror.git"):
            pass
