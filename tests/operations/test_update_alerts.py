"""Offline contract examples for the local alert CLI (issue #1679).

All timestamps and quantities are synthetic literals. Expected counts are hand
counts of the records written in each test; line numbers count from the first
JSONL row. The CLI's diagnostic limit is specified in its README contract.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/operations/update_alerts.py"
spec = importlib.util.spec_from_file_location("update_alerts", SCRIPT)
alerts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alerts)

FAILURE = {
    "source": "maintenance",
    "job": "update-check",
    "status": "fail",
    "ts": "2026-01-01T00:00:00Z",
    "tool": "configured-tool",
    "failure": "synthetic update rejected",
    "rollback": "previous configuration restored",
    "details": "maintainer attention required",
}
ACK_AT = "2026-01-02T00:00:00Z"


@pytest.fixture
def journals(tmp_path):
    events = tmp_path / "notifications.jsonl"
    acknowledgements = tmp_path / "acknowledgements.jsonl"
    events.write_text(json.dumps(FAILURE) + "\n", encoding="utf-8", newline="\n")
    return events, acknowledgements


def pending(journals):
    return alerts.read_pending(*journals)["pending"]


def test_failure_alert_remains_until_acknowledged(journals):
    alert, = pending(journals)
    assert alert["event"] == FAILURE
    assert pending(journals) == [alert]
    assert alerts.acknowledge(*journals, alert["id"], ACK_AT) is True
    assert pending(journals) == []


def test_ack_replay_is_idempotent(journals):
    alert, = pending(journals)
    alerts.acknowledge(*journals, alert["id"], ACK_AT)
    before = journals[1].read_bytes()
    assert alerts.acknowledge(*journals, alert["id"], ACK_AT) is False
    assert journals[1].read_bytes() == before
    with journals[1].open("ab") as stream:
        stream.write(before)
    assert pending(journals) == []
    assert alerts.read_pending(*journals)["diagnostic_count"] == 0


def test_event_journal_is_preserved(journals):
    before = journals[0].read_bytes()
    alert, = pending(journals)
    alerts.acknowledge(*journals, alert["id"], ACK_AT)
    assert journals[0].read_bytes() == before
    assert json.loads(journals[1].read_text(encoding="utf-8")) == {
        "id": alert["id"], "acknowledged_at": ACK_AT,
    }


def test_repeated_ingestion_uses_content_identity(journals):
    original, = pending(journals)
    with journals[0].open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(FAILURE, sort_keys=True, indent=None) + "\n")
    assert pending(journals) == [original]
    alerts.acknowledge(*journals, original["id"], ACK_AT)
    assert pending(journals) == []


def test_distinct_failures_sharing_a_job_label(journals):
    first, = pending(journals)
    other = dict(FAILURE, failure="synthetic rollback rejected", rollback="manual review required")
    with journals[0].open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(other) + "\n")
    first_again, second = pending(journals)
    assert first_again == first
    assert first["id"] != second["id"]
    assert second["event"] == other
    alerts.acknowledge(*journals, first["id"], ACK_AT)
    assert pending(journals) == [second]


def test_success_does_not_clear_a_failure(journals):
    alert, = pending(journals)
    with journals[0].open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(dict(FAILURE, status="pass")) + "\n")
    assert pending(journals) == [alert]


def test_empty_journals_and_missing_acknowledgements(journals):
    assert not journals[1].exists()
    pending(journals)
    assert not journals[1].exists()
    journals[0].write_bytes(b"")
    assert pending(journals) == []


@pytest.mark.parametrize("record", [
    b"not-json", b"[]", b"null", b"{}", b"\xff", b"",
    json.dumps(dict(FAILURE, status="unknown")).encode("utf-8"),
    json.dumps(dict(FAILURE, ts="invalid")).encode("utf-8"),
    *[json.dumps(dict(FAILURE, **{field: []})).encode("utf-8")
      for field in ("source", "tool", "failure", "rollback", "details")],
    *[json.dumps(dict(FAILURE, extra=value)).encode("utf-8")
      for value in (float("nan"), float("inf"), float("-inf"))],
    # The duplicate has the same value: only duplicate-key rejection invalidates it.
    ('{"job":"update-check",' + json.dumps(FAILURE)[1:]).encode("utf-8"),
])
def test_malformed_records_are_explicit_without_payloads(journals, record):
    original = pending(journals)
    with journals[0].open("ab") as stream:
        stream.write(record + b"\n")
    view = alerts.read_pending(*journals)
    assert view["pending"] == original
    assert view["diagnostic_count"] == 1
    assert view["diagnostics"] == [
        {"journal": "notifications", "line": 2, "reason": "invalid event"},
    ]


def test_malformed_acknowledgements_cannot_hide_alerts(journals):
    alert, = pending(journals)
    journals[1].write_text(json.dumps({"id": alert["id"]}) + "\n", encoding="utf-8", newline="\n")
    view = alerts.read_pending(*journals)
    assert view["pending"] == [alert]
    assert view["diagnostics"] == [
        {"journal": "acknowledgements", "line": 1, "reason": "invalid acknowledgement"},
    ]
    before = journals[1].read_bytes()
    with pytest.raises(ValueError, match="malformed records"):
        alerts.acknowledge(*journals, alert["id"], ACK_AT)
    assert journals[1].read_bytes() == before


def test_acknowledgement_append_preserves_existing_bytes(journals):
    # A valid unrelated acknowledgement without a final newline remains intact.
    old = json.dumps({"id": "sha256:" + "a" * 64, "acknowledged_at": ACK_AT}).encode()
    journals[1].write_bytes(old)
    alert, = pending(journals)
    alerts.acknowledge(*journals, alert["id"], ACK_AT)
    assert journals[1].read_bytes().startswith(old + b"\n")
    assert alerts.read_pending(*journals)["diagnostics"] == []
    assert pending(journals) == []


@pytest.mark.parametrize("same_path", ["identical", "symlink", "hardlink"])
def test_journals_must_be_distinct(journals, same_path):
    events, ack = journals
    if same_path == "identical":
        ack = events
    elif same_path == "symlink":
        ack.symlink_to(events)
    else:
        ack.hardlink_to(events)
    before = events.read_bytes()
    with pytest.raises(ValueError, match="distinct"):
        alerts.acknowledge(events, ack, "sha256:" + "a" * 64, ACK_AT)
    assert events.read_bytes() == before


def test_unknown_acknowledgement_is_rejected(journals):
    with pytest.raises(ValueError, match="unknown failure"):
        alerts.acknowledge(*journals, "sha256:" + "a" * 64, ACK_AT)
    assert not journals[1].exists()


def test_invalid_acknowledgement_timestamp_is_rejected(journals):
    alert, = pending(journals)
    with pytest.raises(ValueError, match="timestamp"):
        alerts.acknowledge(*journals, alert["id"], "invalid")
    assert not journals[1].exists()


def test_cli_lists_and_acknowledges_synthetic_example(journals):
    args = [sys.executable, str(SCRIPT), "--notifications", str(journals[0]),
            "--acknowledgements", str(journals[1])]
    listed = subprocess.run(args + ["pending"], capture_output=True, text=True)
    assert listed.returncode == 0
    alert, = json.loads(listed.stdout)["pending"]
    assert alert["event"] == FAILURE
    acked = subprocess.run(args + ["ack", alert["id"], "--at", ACK_AT],
                           capture_output=True, text=True)
    assert acked.returncode == 0
    after = subprocess.run(args + ["pending"], capture_output=True, text=True)
    assert json.loads(after.stdout)["pending"] == []


def test_cli_reports_safe_io_errors(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--notifications", str(tmp_path / "absent"),
         "--acknowledgements", str(tmp_path / "acks"), "pending"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "error: journal I/O failed\n"
    assert str(tmp_path) not in result.stderr


def test_cli_malformed_records_exit_nonzero(journals):
    journals[0].write_text("sensitive-placeholder\n", encoding="utf-8", newline="\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--notifications", str(journals[0]),
         "--acknowledgements", str(journals[1]), "pending"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["diagnostic_count"] == 1
    assert "sensitive-placeholder" not in result.stdout + result.stderr


def test_content_identity_matches_independent_digest(journals):
    # README canonical example; computed separately using sha256sum on the
    # literal compact, sorted UTF-8 JSON, with no trailing newline.
    alert, = pending(journals)
    assert alert["id"] == (
        "sha256:f7a68d7feab5d1e22ad5f28b5fcc396df4b04f5048ace6afa08e434a92e65696"
    )


def test_legacy_writer_fields_are_supported(journals):
    event = {
        "source": "maintenance", "job": "update-check", "status": "fail",
        "ts": "2026-01-01T00:00:00Z", "details": "synthetic failure",
    }
    journals[0].write_text(json.dumps(event) + "\n", encoding="utf-8", newline="\n")
    alert, = pending(journals)
    assert alert["event"] == event
    assert "rollback" not in alert["event"]


def test_changed_timestamp_is_a_distinct_failure(journals):
    first, = pending(journals)
    later = dict(FAILURE, ts="2026-01-02T00:00:00Z")
    with journals[0].open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(later) + "\n")
    alerts.acknowledge(*journals, first["id"], ACK_AT)
    remaining, = pending(journals)
    assert remaining["event"] == later


def test_diagnostics_are_bounded(journals):
    # README contract: twenty diagnostics shown; twenty-one invalid rows counted.
    journals[0].write_bytes(b"invalid\n" * 21)
    view = alerts.read_pending(*journals)
    assert view["pending"] == []
    assert view["diagnostic_count"] == 21
    assert len(view["diagnostics"]) == 20
    assert view["diagnostics"][-1]["line"] == 20


def test_success_only_journal_has_no_alerts(journals):
    journals[0].write_text(json.dumps(dict(FAILURE, status="pass")) + "\n", encoding="utf-8", newline="\n")
    assert pending(journals) == []


@pytest.mark.parametrize("bad_record", [
    '{"id":"bad","acknowledged_at":"2026-01-02T00:00:00Z"}',
    '{"id":"sha256:' + 'a' * 64 + '","acknowledged_at":"invalid"}',
    '[]', 'not-json',
])
def test_invalid_acknowledgement_records_are_explicit(journals, bad_record):
    original = pending(journals)
    journals[1].write_text(bad_record + "\n", encoding="utf-8", newline="\n")
    view = alerts.read_pending(*journals)
    assert view["pending"] == original
    assert view["diagnostic_count"] == 1
    assert view["diagnostics"][0]["journal"] == "acknowledgements"


def test_acknowledgement_replay_survives_event_reformatting(journals):
    alert, = pending(journals)
    alerts.acknowledge(*journals, alert["id"], ACK_AT)
    journals[0].write_text(json.dumps(FAILURE, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    assert pending(journals) == []


def test_cli_requires_explicit_paths():
    result = subprocess.run([sys.executable, str(SCRIPT), "pending"], capture_output=True, text=True)
    # README exit contract: invalid command arguments use exit status two.
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "error: invalid arguments; use --help\n"


@pytest.mark.parametrize("role", ["notifications", "acknowledgements"])
@pytest.mark.parametrize("command", ["pending", "ack"])
def test_cli_contains_symlink_resolution_errors(journals, role, command):
    identity = pending(journals)[0]["id"]
    journals[1].write_text(
        json.dumps({"id": "sha256:" + "a" * 64, "acknowledged_at": ACK_AT}) + "\n",
        encoding="utf-8", newline="\n",
    )
    before = [path.read_bytes() for path in journals]
    index = 0 if role == "notifications" else 1
    original = journals[index]
    preserved = original.with_suffix(".preserved")
    original.rename(preserved)
    original.symlink_to(original.name)
    args = [sys.executable, str(SCRIPT), "--notifications", str(journals[0]),
            "--acknowledgements", str(journals[1]), command]
    if command == "ack":
        args += [identity, "--at", ACK_AT]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert str(original) not in result.stderr
    assert result.stderr == "error: journal path resolution failed\n"
    assert original.is_symlink()
    assert original.readlink() == Path(original.name)
    assert preserved.read_bytes() == before[index]
    assert journals[1 - index].read_bytes() == before[1 - index]
