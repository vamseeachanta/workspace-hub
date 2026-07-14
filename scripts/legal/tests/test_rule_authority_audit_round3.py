"""Runtime regressions from the final Phase A2 adversarial review."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import io
import sys
import uuid
import zipfile
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_github, report_transaction  # noqa: E402
from rule_authority.coverage_contract import REQUIRED_COVERAGE  # noqa: E402
from rule_authority.structural import SensitiveArtifacts  # noqa: E402

KEY = b"k" * 32
PATTERN = b"synthetic-block-value"
SENSITIVE = SensitiveArtifacts(KEY, (PATTERN,), (), frozenset())
REVISION = "12345678-1234-4234-9234-123456789abc"


def _fields(transaction_id: str) -> dict:
    return {
        "api_snapshot_id": "api", "authority_revision": REVISION,
        "coverage_states": {name: "scanned" for name in REQUIRED_COVERAGE},
        "generation": 1, "manifest_mac": "a" * 64, "ref_snapshot_id": "refs",
        "schema_id": "legal-rule-complete-v1", "transaction_id": transaction_id,
    }


def _files() -> dict[str, bytes]:
    return {"coverage.json": b"{}\n", "findings.bin": b"", "reachability.json": b"{}\n"}


@pytest.mark.parametrize(
    "files,file_limit,total_limit",
    [
        ({**_files(), "coverage.json": b"x" * 1001}, 1000, 100_000),
        (_files(), 10_000, 10),
    ],
)
def test_writer_rejects_report_size_limits_before_publication(
        tmp_path: Path, monkeypatch, files: dict[str, bytes],
        file_limit: int, total_limit: int) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    monkeypatch.setattr(report_transaction, "MAX_REPORT_FILE_BYTES", file_limit)
    monkeypatch.setattr(report_transaction, "MAX_REPORT_TOTAL_BYTES", total_limit)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(root, transaction_id, files, _fields(transaction_id), KEY)
    assert list(root.iterdir()) == []


def test_verifier_rejects_same_inode_same_size_change_after_read(
        tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    final = report_transaction.write_report(
        root, transaction_id, _files(), _fields(transaction_id), KEY
    )
    target = final / "coverage.json"
    before = target.stat()
    original = report_transaction._read_file
    calls = 0

    def mutate_after_reads(directory_fd: int, name: str) -> bytes:
        nonlocal calls
        value = original(directory_fd, name)
        calls += 1
        if calls == 4:
            target.write_bytes(b"[]\n")
        return value

    monkeypatch.setattr(report_transaction, "_read_file", mutate_after_reads)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.verify_report(final, KEY)
    after = target.stat()
    assert (after.st_ino, after.st_size) == (before.st_ino, before.st_size)


class FixtureAdapter:
    def __init__(self, pages: dict[str, list[audit_github.ApiPage]]) -> None:
        self.pages = pages

    def snapshot(self) -> str:
        return "stable"

    def page(self, surface: str, cursor: str | None) -> audit_github.ApiPage:
        return self.pages[surface][int(cursor or "0")]


def _zip() -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("safe.bin", b"safe")
    return output.getvalue()


def test_inventory_scans_zip_download_label_and_members() -> None:
    raw = _zip()
    pages = {name: [audit_github.ApiPage(b"safe", None, "etag", 0)]
             for name in audit_github.REQUIRED_SURFACES}
    pages["artifacts"] = [audit_github.ApiPage(
        b"safe", None, "etag", 0, download_links=1,
        downloads=(audit_github.Download(
            PATTERN, raw, len(raw), len(b"safe"), archive_format="zip"
        ),),
    )]
    result = audit_github.inventory(
        FixtureAdapter(pages), SENSITIVE, max_pages=40, max_bytes=1000,
        max_edges=20, max_downloads=5, max_compressed_bytes=1000,
        max_expanded_bytes=1000,
    )
    assert b"artifacts:" + PATTERN in result.private_findings
