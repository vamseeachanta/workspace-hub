"""Public result withholding and private report transaction tests."""

from __future__ import annotations

import json
import os
import stat
import sys
import uuid
from pathlib import Path

import pytest

LEGAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_output, report_transaction  # noqa: E402
from rule_authority.complete import verify_complete  # noqa: E402


KEY = b"r" * 32
REVISION = "12345678-1234-4234-9234-123456789abc"


@pytest.mark.parametrize("rc,verdict", [(0, "clean"), (1, "blocked"), (3, "incomplete"), (4, "error")])
def test_public_result_exact_allowlist(rc: int, verdict: str) -> None:
    raw = audit_output.public_result(
        command="audit-tree", revision=REVISION, generation=7,
        objects_examined=9, coverage="complete", verdict=verdict, rc=rc,
    )
    value = json.loads(raw)
    assert set(value) == {
        "command", "coverage", "generation", "objects_examined", "rc", "revision", "verdict"
    }
    assert raw.endswith("\n")


def test_public_exception_is_fixed_and_withholds_locator_value() -> None:
    secret = "synthetic-secret-fragment"
    locator = "refs/pull/99/head"
    raw = audit_output.public_failure("audit-history", 3, RuntimeError(f"{locator}: {secret}"))
    assert secret not in raw
    assert locator not in raw
    assert raw == '{"command":"audit-history","message":"coverage incomplete","rc":3}\n'


def test_exit_precedence() -> None:
    assert audit_output.combine_rc(1, 3, 0) == 3
    assert audit_output.combine_rc(1, 4, 3) == 4
    assert audit_output.combine_rc(0, 0) == 0


def _complete_fields(transaction_id: str) -> dict:
    return {
        "api_snapshot_id": "api-1", "authority_revision": REVISION,
        "coverage_states": {"git": "scanned"}, "generation": 7,
        "manifest_mac": "a" * 64, "ref_snapshot_id": "refs-1",
        "schema_id": "legal-rule-complete-v1", "transaction_id": transaction_id,
    }


def test_report_transaction_writes_complete_last_and_modes(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    final = report_transaction.write_report(
        root, transaction_id, {"coverage.json": b"{}\n", "findings.bin": b"private"},
        _complete_fields(transaction_id), KEY,
    )
    assert final.name == transaction_id
    assert stat.S_IMODE(final.stat().st_mode) == 0o700
    assert stat.S_IMODE((final / "coverage.json").stat().st_mode) == 0o600
    complete = verify_complete((final / "COMPLETE").read_bytes(), KEY)
    assert [entry["path"] for entry in complete["files"]] == ["coverage.json", "findings.bin"]


def test_report_transaction_no_overwrite_and_rejects_unsafe_names(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    fields = _complete_fields(transaction_id)
    report_transaction.write_report(root, transaction_id, {"a": b"x"}, fields, KEY)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(root, transaction_id, {"a": b"x"}, fields, KEY)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(root, str(uuid.uuid4()), {"../escape": b"x"}, fields, KEY)


def test_report_transaction_failure_never_appears_complete(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError("synthetic disk failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(
            root, transaction_id, {"coverage.json": b"{}"},
            _complete_fields(transaction_id), KEY,
        )
    assert not (root / transaction_id / "COMPLETE").exists()
    incomplete = list(root.glob(".incomplete.*"))
    assert len(incomplete) == 1
    assert not (incomplete[0] / "COMPLETE").exists()


def test_report_root_must_be_private_current_uid(tmp_path: Path) -> None:
    root = tmp_path / "unsafe"
    root.mkdir(mode=0o755)
    transaction_id = str(uuid.uuid4())
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.write_report(
            root, transaction_id, {"a": b"x"}, _complete_fields(transaction_id), KEY
        )


def test_report_reader_rejects_extra_missing_and_changed_files(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir(mode=0o700)
    transaction_id = str(uuid.uuid4())
    final = report_transaction.write_report(
        root, transaction_id, {"coverage.json": b"{}\n"},
        _complete_fields(transaction_id), KEY,
    )
    assert report_transaction.verify_report(final, KEY)["transaction_id"] == transaction_id
    (final / "extra").write_bytes(b"x")
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.verify_report(final, KEY)
    (final / "extra").unlink()
    (final / "coverage.json").write_bytes(b"changed")
    with pytest.raises(report_transaction.ReportTransactionError):
        report_transaction.verify_report(final, KEY)
