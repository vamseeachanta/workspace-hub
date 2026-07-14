from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import audit, codec, coverage, private_io  # noqa: E402


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def test_audit_tree_scans_raw_paths_blobs_and_commit_bytes(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    git(repo, "config", "user.name", "Synthetic")
    (repo / "nested").mkdir()
    (repo / "nested" / "data.bin").write_bytes(b"prefix prohibited suffix")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "synthetic commit")
    oid = git(repo, "rev-parse", "HEAD")
    result = audit.audit_tree(
        repo / ".git",
        oid,
        "refs/heads/master",
        [b"prohibited"],
        {
            "max_blob_bytes": 1024,
            "max_entries": 20,
            "max_findings": 10,
            "max_request_bytes": 4096,
        },
    )
    assert result == {"coverage": "complete", "findings": 1, "objects_examined": 2}


def test_audit_tree_rejects_subset_ref_and_caps(tmp_path):
    with pytest.raises(codec.AuthorityError, match="integrity"):
        audit.audit_tree(
            tmp_path,
            "bad",
            "HEAD",
            [b"x"],
            {
                "max_blob_bytes": 1,
                "max_entries": 1,
                "max_findings": 1,
                "max_request_bytes": 1,
            },
        )


def test_private_transaction_is_no_overwrite_complete_and_atomic(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir()
    identity = {
        "authority_revision": "12345678-1234-4234-9234-123456789abc",
        "generation": 1,
        "manifest_mac": "a" * 64,
    }
    result = private_io.write_complete_transaction(
        parent,
        "12345678-1234-4234-9234-123456789abc",
        {"report.json": b"{}\n"},
        b"k" * 32,
        identity,
    )
    assert (result / "COMPLETE").is_file()
    with pytest.raises(codec.AuthorityError, match="filesystem"):
        private_io.write_complete_transaction(
            parent,
            "12345678-1234-4234-9234-123456789abc",
            {"report.json": b"{}\n"},
            b"k" * 32,
            identity,
        )
    if os.name != "nt":
        assert (result.stat().st_mode & 0o077) == 0


def test_cleanup_only_removes_validated_incomplete_transaction(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir()
    target = parent / ".incomplete.12345678-1234-4234-9234-123456789abc"
    target.mkdir()
    (target / "marker").write_bytes(b"incomplete\n")
    private_io.cleanup_incomplete(parent, "12345678-1234-4234-9234-123456789abc")
    assert not target.exists()


def test_dual_slot_exact_head_and_coverage_matrix():
    current = {"slot": "current", "expected_head_oid": None}
    pending = {"slot": "pending", "expected_head_oid": "e" * 40}
    assert coverage.select_slot(current, pending, "e" * 40) is pending
    assert coverage.select_slot(current, pending, "d" * 40) is current
    scanned = {name: "scanned" for name in coverage.REQUIRED_SURFACES}
    assert coverage.classify_coverage(scanned) == "complete"
    scanned["actions"] = "unknown-residual"
    assert coverage.classify_coverage(scanned) == "residual"
    with pytest.raises(codec.AuthorityError):
        coverage.classify_coverage({"issues": "scanned"})
