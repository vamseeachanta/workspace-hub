"""Offline summary contract for issue #3655, using hand-counted synthetic JSONL.

The existing source declarations are scripts/notify.sh and
scripts/email/state/notifications.py. No producer data is read by these tests.
All numeric expectations below are independent counts of the explicit rows.
"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/productivity/sections/notifications-summary.py"
)

# Seven rows: four unique keys; three replays. Latest A is acknowledged,
# latest B is unread/error, C is unread/info and D is unread/critical.
# Thus three unread: email=one, ci=one, other=one; cron=benchmark=zero.
SYNTHETIC_JSONL = """\
{"event_key":"A","source":"cron","severity":"warning","acknowledged":false}
{"event_key":"B","source":"email","severity":"error","acknowledged":false}
{"event_key":"B","source":"email","severity":"error","acknowledged":false}
{"event_key":"C","source":"ci","severity":"info","acknowledged":false}
{"event_key":"A","source":"cron","severity":"warning","acknowledged":true}
{"event_key":"D","source":"unrecognized","severity":"critical","acknowledged":false}
{"event_key":"B","source":"email","severity":"error","acknowledged":false}
"""


@pytest.fixture
def events_file(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(SYNTHETIC_JSONL, encoding="utf-8")
    return path


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_unread_counts_use_unique_keys(events_file):
    result = run_cli(events_file)
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "input_status": "ok",
        "unique_events": 4,
        "duplicate_records": 3,
        "malformed_records": 0,
        "unread_total": 3,
        "unread_by_severity": {"info": 1, "warning": 0, "error": 1, "critical": 1},
        "unread_by_category": {"email": 1, "cron": 0, "ci": 1, "benchmark": 0, "other": 1},
    }


def test_missing_and_malformed_input_are_explicit(tmp_path, events_file):
    missing = tmp_path / "missing.jsonl"
    result = run_cli(missing)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["input_status"] == "missing"
    assert payload["unread_total"] == payload["malformed_records"] == 0
    assert not missing.exists()
    # One invalid JSON row, one non-object, one absent schema, and one
    # invalid acknowledgement: four malformed records; valid rows survive.
    with events_file.open("a", encoding="utf-8") as handle:
        handle.write('broken\n[]\n{}\n')
        handle.write('{"event_key":"A","severity":"info","acknowledged":"false"}\n')
    result = run_cli(events_file)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["input_status"] == "partial"
    assert payload["malformed_records"] == 4
    assert payload["unread_total"] == 3
    assert str(missing) not in result.stdout + result.stderr


def test_summary_does_not_change_input(tmp_path, events_file):
    before = events_file.read_bytes()
    siblings = set(tmp_path.iterdir())
    first = run_cli(events_file)
    second = run_cli(events_file)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert events_file.read_bytes() == before
    assert set(tmp_path.iterdir()) == siblings


def test_output_is_allowlisted_and_offline(tmp_path, monkeypatch, capsys):
    spec = importlib.util.spec_from_file_location("notification_summary", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def forbidden(*args, **kwargs):
        pytest.fail("network or process execution attempted")

    import socket
    import urllib.request

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    private_path = tmp_path / "private-record.jsonl"
    record = {
        "event_key": "private-key",
        "source": str(private_path),
        "severity": "warning",
        "acknowledged": False,
        "message": "private message text",
        "person": "private identity",
        "details": {"path": str(private_path)},
    }
    private_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    assert module.main([str(private_path)]) == 0
    out, err = capsys.readouterr()
    # One valid unread warning, mapped to the fixed fallback category.
    assert json.loads(out)["unread_by_category"]["other"] == 1
    assert err == ""
    for private_value in (str(private_path), "private-key", "private message text", "private identity"):
        assert private_value not in out


@pytest.mark.parametrize(
    "raw",
    [
        '{"event_key":"A","severity":"info","acknowledged":0}',
        '{"event_key":"A","severity":"unknown","acknowledged":false}',
        '{"event_key":" ","severity":"info","acknowledged":false}',
        '{"event_key":[],"severity":"info","acknowledged":false}',
        '{"event_key":"A","severity":[],"acknowledged":false}',
        '{"event_key":"A","severity":"info","acknowledged":false,"source":[]}',
        '{"event_key":"A","severity":"info","acknowledged":false,"acknowledged":true}',
        '{"event_key":"A","severity":"info","acknowledged":false,"details":NaN}',
        '{"event_key":"A","severity":"info","acknowledged":false,"details":Infinity}',
        '{"event_key":"A","severity":"info","acknowledged":false,"details":-Infinity}',
    ],
)
def test_invalid_record_is_counted_without_disclosure(tmp_path, raw):
    path = tmp_path / "invalid.jsonl"
    path.write_text(raw + "\n", encoding="utf-8")
    result = run_cli(path)
    payload = json.loads(result.stdout)
    # One malformed row, no accepted events and no unread events.
    assert result.returncode == 1
    assert payload["malformed_records"] == 1
    assert payload["unique_events"] == payload["unread_total"] == 0
    assert raw not in result.stdout + result.stderr


def test_valid_replays_replace_severity_and_acknowledgement(tmp_path):
    path = tmp_path / "replays.jsonl"
    # One unique key, two replays; the final valid record reopens it as
    # one unread critical event in the benchmark category.
    path.write_text(
        '{"event_key":"A","severity":"info","acknowledged":false}\n'
        '{"event_key":"A","severity":"error","acknowledged":true}\n'
        '{"event_key":"A","severity":"critical","acknowledged":false,"source":"benchmark"}\n',
        encoding="utf-8",
    )
    payload = json.loads(run_cli(path).stdout)
    assert payload["unique_events"] == payload["unread_total"] == 1
    assert payload["duplicate_records"] == 2
    assert payload["unread_by_severity"] == {"info": 0, "warning": 0, "error": 0, "critical": 1}
    assert payload["unread_by_category"]["benchmark"] == 1


def test_empty_file_is_distinct_from_missing(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_bytes(b"")
    result = run_cli(path)
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["input_status"] == "ok"
    assert payload["unique_events"] == payload["unread_total"] == 0


def test_bad_encoding_and_blank_lines_are_malformed(tmp_path):
    path = tmp_path / "bytes.jsonl"
    # Two malformed lines, then one valid unread info event.
    path.write_bytes(b"\xff\n\n" + SYNTHETIC_JSONL.splitlines()[3].encode() + b"\n")
    result = run_cli(path)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["malformed_records"] == 2
    assert payload["unread_total"] == 1
    assert result.stderr == ""


def test_unreadable_path_and_argument_errors_are_neutral(tmp_path):
    result = run_cli(tmp_path)
    assert result.returncode == 1
    assert json.loads(result.stdout)["input_status"] == "unreadable"
    assert result.stderr == ""
    # Missing input and an unknown option use argparse's error status, two.
    for args in ([], ["--private-option", str(tmp_path)]):
        result = run_cli(*args)
        assert result.returncode == 2
        assert result.stdout == ""
        assert result.stderr == "error: expected one input file argument\n"
