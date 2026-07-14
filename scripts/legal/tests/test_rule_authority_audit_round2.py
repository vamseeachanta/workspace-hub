"""Runtime regressions from the second Phase A2 adversarial review."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import io
import os
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_git, audit_github, report_transaction  # noqa: E402
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
    _git(source, "commit", "-qm", "safe branch")
    return source, _git(source, "rev-parse", "HEAD").decode().strip()


def _private_modes(root: Path) -> None:
    for directory, directories, files in os.walk(root):
        os.chmod(directory, 0o700)
        for name in directories:
            os.chmod(Path(directory) / name, 0o700)
        for name in files:
            os.chmod(Path(directory) / name, 0o600)


def _mirror(tmp_path: Path) -> Path:
    mirror = tmp_path / "mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    _private_modes(mirror)
    return mirror


def _audit(mirror: Path, source: Path, max_edges: int = 80):
    return audit_git.audit_history(
        mirror, str(source), SENSITIVE, api_discovered_oids=(), max_refs=20,
        max_entries=20, max_blob_bytes=100, max_objects=40, max_edges=max_edges,
    )


def test_history_includes_advertised_detached_head(tmp_path: Path) -> None:
    source, branch_oid = _source(tmp_path)
    (source / "safe").write_bytes(PATTERN)
    _git(source, "add", "safe")
    detached = _git(source, "commit-tree", _git(source, "write-tree").strip().decode(),
                    "-m", "detached").strip().decode()
    _git(source, "checkout", "-q", "--detach", detached)
    assert detached != branch_oid
    result = _audit(_mirror(tmp_path), source)
    assert result.verdict == "blocked"
    assert any(edge[0] == b"HEAD" and edge[1] == detached.encode() for edge in result.edges)


class FixtureAdapter:
    def __init__(self, pages: dict[str, list[audit_github.ApiPage]]) -> None:
        self.pages = pages

    def snapshot(self) -> str:
        return "stable"

    def page(self, surface: str, cursor: str | None) -> audit_github.ApiPage:
        return self.pages[surface][int(cursor or "0")]


def _pages() -> dict[str, list[audit_github.ApiPage]]:
    return {name: [audit_github.ApiPage(b"safe", None, "etag", 0)]
            for name in audit_github.REQUIRED_SURFACES}


def _zip(entries: list[tuple[str, bytes]]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)
    return output.getvalue()


def test_inventory_scans_expanded_zip_download_content() -> None:
    raw = _zip([("inside.bin", PATTERN)])
    pages = _pages()
    pages["artifacts"] = [audit_github.ApiPage(
        b"safe", None, "etag", 0, download_links=1,
        downloads=(audit_github.Download(
            b"archive", raw, len(raw), len(PATTERN), archive_format="zip"
        ),),
    )]
    result = audit_github.inventory(
        FixtureAdapter(pages), SENSITIVE, max_pages=40, max_bytes=1000,
        max_edges=20, max_downloads=5, max_compressed_bytes=1000,
        max_expanded_bytes=1000,
    )
    assert b"artifacts:archive:inside.bin" in result.private_findings


@pytest.mark.parametrize("name", ["a//b", "a/./b", "a/b/../c"])
def test_zip_rejects_noncanonical_alias_names(name: str) -> None:
    raw = _zip([(name, b"safe")])
    with pytest.raises(audit_github.CoverageError):
        audit_github.scan_zip(
            raw, SENSITIVE, max_entries=5, max_compressed_bytes=1000,
            max_expanded_bytes=1000, max_ratio=20, max_depth=4,
        )


def _fields(transaction_id: str) -> dict:
    return {
        "api_snapshot_id": "api", "authority_revision": REVISION,
        "coverage_states": {name: "scanned" for name in REQUIRED_COVERAGE},
        "generation": 1, "manifest_mac": "a" * 64, "ref_snapshot_id": "refs",
        "schema_id": "legal-rule-complete-v1", "transaction_id": transaction_id,
    }


def _files() -> dict[str, bytes]:
    return {"coverage.json": b"{}\n", "findings.bin": b"", "reachability.json": b"{}\n"}


def test_rollback_collision_cannot_leave_verifiable_final(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    original = os.fsync
    calls = 0

    def collide_then_fail(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == 6:
            (root / f".incomplete.{transaction_id}").mkdir(mode=0o700)
            raise OSError("post-publication failure")
        original(descriptor)

    monkeypatch.setattr(os, "fsync", collide_then_fail)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(root, transaction_id, _files(), _fields(transaction_id), KEY)
    final = root / transaction_id
    assert not final.exists()


def test_report_read_enforces_cumulative_cap_and_stable_inventory(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    final = report_transaction.write_report(root, transaction_id, _files(), _fields(transaction_id), KEY)
    monkeypatch.setattr(report_transaction, "MAX_REPORT_TOTAL_BYTES", 4)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.verify_report(final, KEY)
    monkeypatch.setattr(report_transaction, "MAX_REPORT_TOTAL_BYTES", 1000)
    original = report_transaction._read_file
    calls = 0

    def add_extra_after_last(directory_fd: int, name: str) -> bytes:
        nonlocal calls
        value = original(directory_fd, name)
        calls += 1
        if calls == 4:
            (final / "extra").write_bytes(b"x")
        return value

    monkeypatch.setattr(report_transaction, "_read_file", add_extra_after_last)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.verify_report(final, KEY)


def test_report_read_rejects_concurrent_growth(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    target = root / "value"
    target.write_bytes(b"1234")
    os.chmod(target, 0o600)
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    original = os.read
    grown = False

    def grow_after_first(file_descriptor: int, size: int) -> bytes:
        nonlocal grown
        value = original(file_descriptor, size)
        if not grown:
            grown = True
            with target.open("ab") as stream:
                stream.write(b"5678")
        return value

    monkeypatch.setattr(os, "read", grow_after_first)
    monkeypatch.setattr(report_transaction, "MAX_REPORT_FILE_BYTES", 4)
    try:
        with pytest.raises(report_transaction.ReportTransactionError):
            report_transaction._read_file(descriptor, "value")
    finally:
        os.close(descriptor)


def test_history_rejects_unreachable_objects_and_nonprivate_modes(tmp_path: Path) -> None:
    source, _ = _source(tmp_path)
    mirror = _mirror(tmp_path)
    _git(mirror, "hash-object", "-w", "--stdin", input_bytes=PATTERN)
    with pytest.raises(audit_git.CoverageError):
        _audit(mirror, source)
    mirror = tmp_path / "mode-mirror.git"
    _git(tmp_path, "init", "--bare", "-q", str(mirror))
    os.chmod(mirror, 0o700)
    with pytest.raises(audit_git.CoverageError):
        _audit(mirror, source)


def test_index_edge_budget_accepts_documented_entry_limit(tmp_path: Path) -> None:
    source, _ = _source(tmp_path)
    for index in range(4):
        (source / f"file-{index}").write_bytes(b"safe")
    _git(source, "add", "--", "file-0", "file-1", "file-2", "file-3")
    result = audit_git.audit_index(source, SENSITIVE, max_entries=5, max_blob_bytes=100)
    assert result.verdict == "clean"
    assert result.objects_examined == 1
    assert len(result.edges) == 10
