"""Exact post-write transaction state coverage for cron_apply."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "cron_apply_exact_state", REPO / "scripts" / "cron" / "cron_apply.py"
)
ca = importlib.util.module_from_spec(spec)
sys.modules["cron_apply_exact_state"] = ca
spec.loader.exec_module(ca)


def _transaction_fixture(monkeypatch, tmp_path, reads, write_fn=None):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "backups")
    monkeypatch.setattr(ca.ct, "plan_cutover", lambda *_a, **_k: {
        "new_text": "planned\n", "preserved": [], "uncataloged": [],
        "conflicts": [], "abort_reason": None,
    })
    iterator = iter(reads)
    writes = []

    def _write(text):
        writes.append(text)
        if write_fn:
            write_fn(text, len(writes))

    result = ca.run_cutover(
        "dev-primary", True, "transaction", _read=lambda: next(iterator),
        _write=_write, _daemons=lambda _pattern: False,
    )
    return result, writes


def _patched_transaction(monkeypatch, tmp_path, reads, write=None):
    iterator = iter(reads)

    def _read():
        try:
            value = next(iterator)
        except StopIteration as exc:
            raise ca.CronReadError("private read detail") from exc
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "backups")
    monkeypatch.setattr(ca.ct, "plan_cutover", lambda *_a, **_k: {
        "new_text": "planned\n", "preserved": [], "abort_reason": None,
    })
    writes = []

    def _write(text):
        writes.append(text)
        if write:
            write(text, len(writes))

    result = ca.run_cutover(
        "dev-primary", True, "state", _read=_read, _write=_write,
        _daemons=lambda _pattern: False,
    )
    return result, writes


def test_applied_requires_exact_post_write_bytes(monkeypatch, tmp_path):
    result, writes = _transaction_fixture(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", "planned\nextra\n", "planned\nextra\n", "baseline\n"],
    )
    assert result["status"] == "rolled-back"
    assert writes == ["planned\n", "baseline\n"]
    assert "planned\n" not in str(result)
    assert result["planned"]["bytes"] == len("planned\n".encode())


@pytest.mark.parametrize(
    ("reads", "status", "writes"),
    [
        (["baseline\n", "baseline\n", "corrupt\n", "corrupt\n", "baseline\n"],
         "rolled-back", ["planned\n", "baseline\n"]),
        (["baseline\n", "baseline\n", "corrupt\n", "corrupt\n", "corrupt\n"],
         "rollback-failed", ["planned\n", "baseline\n"]),
        (["baseline\n", "baseline\n", "corrupt\n", "third-party\n"],
         "rollback-aborted", ["planned\n"]),
    ],
)
def test_corruption_restore_outcomes(monkeypatch, tmp_path, reads, status, writes):
    result, actual_writes = _transaction_fixture(monkeypatch, tmp_path, reads)
    assert result["status"] == status
    assert actual_writes == writes


def test_rollback_cas_read_exception_is_indeterminate(monkeypatch, tmp_path):
    result, writes = _patched_transaction(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", "corrupt\n", ca.CronReadError("secret")],
    )
    assert result["status"] == "rollback-indeterminate"
    assert writes == ["planned\n"]
    assert "secret" not in str(result)


@pytest.mark.parametrize(
    ("observed", "expected_status"),
    [("baseline\n", "write-failed-no-change"),
     ("planned\n", "write-error-state-exact")],
)
def test_initial_write_exception_reports_observed_state(
    monkeypatch, tmp_path, observed, expected_status
):
    def fail_initial(_text, call_number):
        if call_number == 1:
            raise OSError("write detail must stay bounded")

    result, writes = _transaction_fixture(
        monkeypatch, tmp_path, ["baseline\n", "baseline\n", observed], fail_initial
    )
    assert result["status"] == expected_status
    assert len(writes) == 1
    assert "write detail must stay bounded" not in str(result)


def test_initial_write_exception_with_partial_state_rolls_back(monkeypatch, tmp_path):
    def fail_initial(_text, call_number):
        if call_number == 1:
            raise OSError("partial write")

    result, writes = _transaction_fixture(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", "partial\n", "partial\n", "baseline\n"],
        fail_initial,
    )
    assert result["status"] == "rolled-back"
    assert writes == ["planned\n", "baseline\n"]


@pytest.mark.parametrize("write_fails", [False, True])
def test_verification_read_exception_is_indeterminate(
    monkeypatch, tmp_path, write_fails
):
    def write(_text, call_number):
        if write_fails and call_number == 1:
            raise OSError("unbounded write detail")

    result, writes = _patched_transaction(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", ca.CronReadError("unbounded read detail")],
        write,
    )
    assert result["status"] == "verification-indeterminate"
    assert writes == ["planned\n"]
    assert "unbounded" not in str(result)


@pytest.mark.parametrize(
    ("after_error", "expected_status"),
    [("baseline\n", "rolled-back-with-write-error"),
     ("corrupt\n", "rollback-failed"),
     ("third-party\n", "rollback-aborted")],
)
def test_rollback_write_exception_reports_observed_state(
    monkeypatch, tmp_path, after_error, expected_status
):
    def fail_rollback(_text, call_number):
        if call_number == 2:
            raise OSError("rollback write failed")

    result, writes = _transaction_fixture(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", "corrupt\n", "corrupt\n", after_error],
        fail_rollback,
    )
    assert result["status"] == expected_status
    assert len(writes) == 2


def test_rollback_verification_read_exception_is_indeterminate(monkeypatch, tmp_path):
    result, writes = _patched_transaction(
        monkeypatch, tmp_path,
        ["baseline\n", "baseline\n", "corrupt\n", "corrupt\n",
         ca.CronReadError("rollback read detail")],
    )
    assert result["status"] == "rollback-indeterminate"
    assert writes == ["planned\n", "baseline\n"]
    assert "rollback read detail" not in str(result)


@pytest.mark.parametrize(
    "status",
    [
        "rolled-back", "rollback-failed", "rollback-aborted",
        "rollback-indeterminate", "write-failed-no-change",
        "write-error-state-exact", "verification-indeterminate",
        "rolled-back-with-write-error",
    ],
)
def test_main_returns_nonzero_for_transaction_failures(monkeypatch, status):
    registry = {"machines": {"m1": {"hostname": "m1"}}}
    monkeypatch.setattr(ca, "_load", lambda _path: registry)
    monkeypatch.setattr(ca.socket, "gethostname", lambda: "m1")
    monkeypatch.setattr(ca, "run_cutover", lambda *_a, **_k: {"status": status})
    assert ca.main(["--machine", "m1", "--apply", "--json"]) == 2


@pytest.mark.parametrize("status", ["applied", "dry-run"])
def test_main_returns_zero_for_success_states(monkeypatch, status):
    registry = {"machines": {"m1": {"hostname": "m1"}}}
    monkeypatch.setattr(ca, "_load", lambda _path: registry)
    monkeypatch.setattr(ca.socket, "gethostname", lambda: "m1")
    monkeypatch.setattr(ca, "run_cutover", lambda *_a, **_k: {"status": status})
    assert ca.main(["--machine", "m1", "--json"]) == 0
