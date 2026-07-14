"""Additional fail-closed regressions found during A2 fix hardening."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_git, report_transaction  # noqa: E402
from rule_authority.coverage_contract import REQUIRED_COVERAGE  # noqa: E402
from rule_authority.structural import SensitiveArtifacts  # noqa: E402

KEY = b"k" * 32
PATTERN = b"synthetic-block-value"
SENSITIVE = SensitiveArtifacts(KEY, (PATTERN,), (), frozenset())
REVISION = "12345678-1234-4234-9234-123456789abc"


def _git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=repo, input=input_bytes, capture_output=True, check=True
    ).stdout


def _source(tmp_path: Path) -> tuple[Path, str]:
    source = tmp_path / "source"
    source.mkdir()
    _git(source, "init", "-q")
    _git(source, "config", "user.name", "Synthetic")
    _git(source, "config", "user.email", "synthetic@example.invalid")
    (source / "safe").write_bytes(b"safe")
    _git(source, "add", "safe")
    _git(source, "commit", "-qm", "safe")
    return source, _git(source, "rev-parse", "HEAD").decode().strip()


def _mirror(tmp_path: Path) -> Path:
    mirror = tmp_path / "mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    os.chmod(mirror, 0o700)
    return mirror


def _audit(mirror: Path, source: Path):
    return audit_git.audit_history(
        mirror, str(source), SENSITIVE, api_discovered_oids=(), max_refs=20,
        max_entries=20, max_blob_bytes=100, max_objects=40, max_edges=80,
    )


def test_history_requires_fresh_mirror_without_remote_or_local_refs(tmp_path: Path) -> None:
    source, oid = _source(tmp_path)
    mirror = _mirror(tmp_path)
    _git(mirror, "remote", "add", "origin", str(source))
    with pytest.raises(audit_git.CoverageError):
        _audit(mirror, source)
    _git(mirror, "remote", "remove", "origin")
    _git(mirror, "fetch", str(source), f"{oid}:refs/heads/stale")
    with pytest.raises(audit_git.CoverageError):
        _audit(mirror, source)


def test_index_scans_gitlink_path_without_walking_foreign_commit(tmp_path: Path) -> None:
    source, oid = _source(tmp_path)
    entry = b"160000 commit " + oid.encode() + b"\t" + PATTERN + b"\x00"
    tree = _git(source, "mktree", "-z", input_bytes=entry).strip()
    _git(source, "read-tree", tree.decode())
    result = audit_git.audit_index(source, SENSITIVE, max_entries=10, max_blob_bytes=100)
    assert result.verdict == "blocked"


def _fields(transaction_id: str) -> dict:
    return {
        "api_snapshot_id": "api", "authority_revision": REVISION,
        "coverage_states": {name: "scanned" for name in REQUIRED_COVERAGE},
        "generation": 1, "manifest_mac": "a" * 64, "ref_snapshot_id": "refs",
        "schema_id": "legal-rule-complete-v1", "transaction_id": transaction_id,
    }


def _files() -> dict[str, bytes]:
    return {"coverage.json": b"{}\n", "findings.bin": b"", "reachability.json": b"{}\n"}


def test_report_rejects_oversize_before_read(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    path = root / "oversize"
    path.write_bytes(b"")
    os.chmod(path, 0o600)
    os.truncate(path, report_transaction.MAX_REPORT_FILE_BYTES + 1)
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    monkeypatch.setattr(os, "read", lambda *_args: pytest.fail("oversize file was read"))
    try:
        with pytest.raises(report_transaction.ReportTransactionError):
            report_transaction._read_file(descriptor, "oversize")
    finally:
        os.close(descriptor)


def test_prepare_closes_child_descriptor_on_write_failure(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    original = report_transaction._write_file
    calls = 0

    def fail_second(descriptor: int, name: str, payload: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic write failure")
        original(descriptor, name, payload)

    monkeypatch.setattr(report_transaction, "_write_file", fail_second)
    before = len(os.listdir(os.path.join(os.sep, "proc", "self", "fd")))
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(root, transaction_id, _files(), _fields(transaction_id), KEY)
    after = len(os.listdir(os.path.join(os.sep, "proc", "self", "fd")))
    assert after == before
