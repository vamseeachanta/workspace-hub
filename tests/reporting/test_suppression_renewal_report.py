"""Synthetic decision tables for the suppression renewal report.

Basis: issue 2191's supplied precedence and explicit-horizon contract. Dates,
counts and identifiers below are invented fixtures. Expected counts are hand
tallies of the listed rows; time differences are calculated in each test.
"""

import copy
import importlib
import io
import json
import socket
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


AS_OF = datetime.fromisoformat("2026-10-15T12:00:00+00:00")
# Hand calculation: two hours = 2 * 60 * 60 = 7200 seconds.
HORIZON = timedelta(hours=2)


def module():
    return importlib.import_module("reporting.suppression_renewal_report")


def record(suppression_id="suppression-a", **changes):
    value = {
        "suppression_id": suppression_id,
        "provider": "provider-a",
        "reason_code": "unresolved-read",
        "responsible_role": "maintainer",
        "reviewer_role": "reviewer",
        "expiry": "2026-10-15T15:00:00Z",
        "last_seen_run": "run-a",
        "unresolved_count": 1,
        "renewal_count": 0,
    }
    value.update(changes)
    return value


@pytest.mark.parametrize(
    "expiry,reviewer,count,state,flags",
    [
        # Expiry at the reference instant is expired, even with other flags.
        ("2026-10-15T12:00:00Z", None, 0, "expired",
         ["expired", "needs-re-review", "no-longer-observed"]),
        ("2026-10-15T11:59:59.999999Z", "reviewer", 1, "expired", ["expired"]),
        # Missing review outranks zero count and the inclusive horizon boundary.
        ("2026-10-15T14:00:00Z", None, 0, "needs-re-review",
         ["needs-re-review", "no-longer-observed", "due-soon"]),
        ("2026-10-15T15:00:00Z", None, 1, "needs-re-review", ["needs-re-review"]),
        ("2026-10-15T14:00:00Z", "reviewer", 0, "no-longer-observed",
         ["no-longer-observed", "due-soon"]),
        ("2026-10-15T15:00:00Z", "reviewer", 0, "no-longer-observed",
         ["no-longer-observed"]),
        ("2026-10-15T12:00:00.000001Z", "reviewer", 1, "due-soon", ["due-soon"]),
        ("2026-10-15T14:00:00Z", "reviewer", 1, "due-soon", ["due-soon"]),
        ("2026-10-15T14:00:00.000001Z", "reviewer", 1, "current", []),
    ],
)
def test_each_state_and_precedence(expiry, reviewer, count, state, flags):
    report = module().build_report(
        [record(expiry=expiry, reviewer_role=reviewer, unresolved_count=count)],
        as_of=AS_OF, due_soon=HORIZON,
    )
    row, = report["queue"]
    assert row["state"] == state
    assert row["flags"] == flags


def test_due_soon_horizon_is_explicit_and_timezone_normalized():
    api = module()
    # 16:00 at +02:00 = 14:00 UTC, exactly two hours after 12:00 UTC.
    # 09:00 at -05:00 is the same instant and must produce identical output.
    first = api.build_report(
        [record(expiry="2026-10-15T16:00:00+02:00")],
        as_of=AS_OF, due_soon=HORIZON,
    )
    assert first == api.build_report(
        [record(expiry="2026-10-15T09:00:00-05:00")],
        as_of=AS_OF, due_soon=HORIZON,
    )
    assert first["as_of"] == "2026-10-15T12:00:00Z"
    assert first["due_soon_seconds"] == 7200
    assert first["queue"][0]["expiry"] == "2026-10-15T14:00:00Z"
    assert first["queue"][0]["state"] == "due-soon"
    # Two hours exceeds a caller's one-hour horizon, or a zero horizon.
    for horizon in [timedelta(hours=1), timedelta(0)]:
        assert api.build_report(
            [record(expiry="2026-10-15T16:00:00+02:00")],
            as_of=AS_OF, due_soon=horizon,
        )["queue"][0]["state"] == "current"
    with pytest.raises(TypeError):
        api.build_report([record()], as_of=AS_OF)
    with pytest.raises(TypeError):
        api.build_report([record()], due_soon=HORIZON)


def test_digest_groups_and_order_are_deterministic():
    rows = [
        record("suppression-d", provider="provider-b", renewal_count=2),
        record("suppression-b", expiry="2026-10-15T13:00:00Z"),
        record("suppression-c", reviewer_role=None, renewal_count=2,
               expiry="2026-10-15T11:00:00Z", unresolved_count=0),
        record("suppression-a", expiry="2026-10-15T13:00:00Z"),
        record("suppression-e", reviewer_role=None, renewal_count=2),
    ]
    api = module()
    report = api.build_report(rows, as_of=AS_OF, due_soon=HORIZON)
    # Hand tally: two due-soon, one expired, one missing review, one current.
    # Missing-review flags occur twice; zero-observed occurs once.
    assert report["digest"] == {
        "total": 5,
        "state_counts": {"expired": 1, "needs-re-review": 1, "due-soon": 2, "current": 1},
        "flag_counts": {"expired": 1, "needs-re-review": 2,
                        "no-longer-observed": 1, "due-soon": 2},
        "groups": [
            {"provider": "provider-a", "reviewer_role": None, "renewal_count": 2,
             "count": 2, "state_counts": {"expired": 1, "needs-re-review": 1},
             "flag_counts": {"expired": 1, "needs-re-review": 2, "no-longer-observed": 1}},
            {"provider": "provider-a", "reviewer_role": "reviewer", "renewal_count": 0,
             "count": 2, "state_counts": {"due-soon": 2}, "flag_counts": {"due-soon": 2}},
            {"provider": "provider-b", "reviewer_role": "reviewer", "renewal_count": 2,
             "count": 1, "state_counts": {"current": 1}, "flag_counts": {}},
        ],
    }
    assert [row["suppression_id"] for row in report["queue"]] == [
        "suppression-c", "suppression-e", "suppression-a", "suppression-b", "suppression-d",
    ]
    for reordered in [list(reversed(rows)), rows[2:] + rows[:2]]:
        assert report == api.build_report(reordered, as_of=AS_OF, due_soon=HORIZON)
        assert api.render_report(rows, as_of=AS_OF, due_soon=HORIZON) == api.render_report(
            reordered, as_of=AS_OF, due_soon=HORIZON,
        )
    # Exact same-state sorting: expiry, provider, suppression id.
    tied = [record("suppression-z"), record("suppression-a"),
            record("suppression-c", provider="provider-b"),
            record("suppression-b", expiry="2026-10-15T14:30:00Z")]
    assert [row["suppression_id"] for row in api.build_report(
        tied, as_of=AS_OF, due_soon=HORIZON,
    )["queue"]] == ["suppression-b", "suppression-a", "suppression-z", "suppression-c"]


@pytest.mark.parametrize("field", list(record()))
def test_malformed_input_is_rejected_when_required_field_is_absent(field):
    row = record()
    del row[field]
    with pytest.raises(ValueError):
        module().build_report([row], as_of=AS_OF, due_soon=HORIZON)


@pytest.mark.parametrize("changes", [
    {"suppression_id": " "}, {"provider": None}, {"reason_code": []},
    {"responsible_role": ""}, {"reviewer_role": ""}, {"reviewer_role": False},
    {"last_seen_run": None}, {"unresolved_count": -1}, {"unresolved_count": True},
    {"unresolved_count": 1.5}, {"renewal_count": -1}, {"renewal_count": False},
    {"renewal_count": "2"}, {"expiry": None}, {"expiry": "2026-02-30T12:00:00Z"},
    {"expiry": "2026-10-15"}, {"expiry": "2026-10-15T12:00:00"},
    {"expiry": "2026-10-15 12:00:00Z"}, {"expiry": "2026-10-15T12:00:00+24:00"},
    {"expiry": "2026-10-15T12:00:00+01:60"},
    {"expiry": "0001-01-01T00:00:00+01:00"},
    {"expiry": "2026-10-15T12:00:00.1234567Z"}, {"unexpected": "value"},
    {"provider": "bad\nvalue"}, {"provider": "\ud800"},
])
def test_malformed_input_is_rejected(changes):
    with pytest.raises(ValueError):
        module().build_report([record(**changes)], as_of=AS_OF, due_soon=HORIZON)


@pytest.mark.parametrize("rows", [None, {}, "records", [None], [[]], [record(), record()]])
def test_malformed_record_collection_is_rejected(rows):
    with pytest.raises(ValueError):
        module().build_report(rows, as_of=AS_OF, due_soon=HORIZON)


@pytest.mark.parametrize("as_of,horizon", [
    (None, HORIZON), ("2026-10-15T12:00:00Z", HORIZON),
    (datetime.fromisoformat("2026-10-15T12:00:00"), HORIZON),
    (datetime.fromisoformat("2026-10-15T14:00:00+02:00"), HORIZON),
    (AS_OF, None), (AS_OF, 7200), (AS_OF, timedelta(microseconds=-1)),
])
def test_malformed_time_policy_is_rejected(as_of, horizon):
    with pytest.raises(ValueError):
        module().build_report([record()], as_of=as_of, due_soon=horizon)


def test_empty_report_and_responsibility_metadata():
    api = module()
    assert api.build_report([], as_of=AS_OF, due_soon=HORIZON) == {
        "as_of": "2026-10-15T12:00:00Z", "due_soon_seconds": 7200,
        "queue": [], "digest": {"total": 0, "state_counts": {}, "flag_counts": {}, "groups": []},
    }
    value = record(responsible_role="maintainer")
    row, = api.build_report([value], as_of=AS_OF, due_soon=HORIZON)["queue"]
    assert row == {**value, "state": "current", "flags": []}


def test_fractional_expiry_and_numeric_recurrence_sorting():
    # .5 seconds follows the whole-second instant; ten renewals follow two.
    # These literals catch lexical sorting of timestamp text or renewal counts.
    rows = [record("suppression-a", expiry="2026-10-15T13:00:00.5Z", renewal_count=2),
            record("suppression-b", expiry="2026-10-15T13:00:00Z", renewal_count=10)]
    report = module().build_report(rows, as_of=AS_OF, due_soon=HORIZON)
    assert [row["suppression_id"] for row in report["queue"]] == ["suppression-b", "suppression-a"]
    assert [group["renewal_count"] for group in report["digest"]["groups"]] == [2, 10]


def test_report_has_no_side_effects(tmp_path, monkeypatch, capsys):
    api = module()
    # Exercise offset normalization while all external access is forbidden.
    rows = [record(expiry="2026-10-15T17:00:00+02:00")]
    original = copy.deepcopy(rows)
    marker = tmp_path / "inventory.json"
    marker.write_text("unchanged", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("report attempted external access")

    # Reading files, launching commands or connecting to a service is forbidden.
    with monkeypatch.context() as context:
        context.setattr("builtins.open", forbidden)
        context.setattr(io, "open", forbidden)
        context.setattr(subprocess, "Popen", forbidden)
        context.setattr(socket, "socket", forbidden)
        output = api.render_report(rows, as_of=AS_OF, due_soon=HORIZON)
    assert json.loads(output) == api.build_report(rows, as_of=AS_OF, due_soon=HORIZON)
    assert rows == original
    assert marker.read_text(encoding="utf-8") == "unchanged"
    assert list(tmp_path.iterdir()) == [marker]
    assert capsys.readouterr() == ("", "")
    result = api.build_report(rows, as_of=AS_OF, due_soon=HORIZON)
    result["queue"][0]["renewal_count"] = 99  # Synthetic mutation probe.
    assert rows == original


def test_cli_emits_json_from_explicit_stdin(monkeypatch, capsys):
    api = module()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps([record()])))
    assert api.main(["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "7200"]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == api.build_report([record()], as_of=AS_OF, due_soon=HORIZON)


def test_script_entrypoint_reads_only_stdin(tmp_path):
    script = Path(__file__).resolve().parents[2] / "scripts/reporting/suppression_renewal_report.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--as-of", "2026-10-15T12:00:00Z",
         "--due-soon-seconds", "7200"],
        input="[]", text=True, capture_output=True, cwd=tmp_path, check=False,
    )
    assert completed.returncode == 0
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == {
        "as_of": "2026-10-15T12:00:00Z", "due_soon_seconds": 7200,
        "queue": [], "digest": {"total": 0, "state_counts": {}, "flag_counts": {}, "groups": []},
    }
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("raw,args", [
    ("[]", []), ("[]", ["--as-of", "2026-10-15T12:00:00Z"]),
    ("[]", ["--as-of", "invalid", "--due-soon-seconds", "7200"]),
    ("[]", ["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "-1"]),
    ("[]", ["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "1e999"]),
    ("[]", ["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "0.5"]),
    ("[]", ["--as-of", "2026-10-15T14:00:00+02:00", "--due-soon-seconds", "7200"]),
    ("[]", ["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "999999999999999999"]),
    ('[{"provider":"a","provider":"b"}]', None),
    ("[NaN]", None), ("[Infinity]", None), ("{", None),
])
def test_cli_rejects_ambiguous_json_and_missing_policy(raw, args, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(raw))
    if args is None:
        args = ["--as-of", "2026-10-15T12:00:00Z", "--due-soon-seconds", "7200"]
    with pytest.raises(SystemExit) as error:
        module().main(args)
    # argparse's documented command-usage error status is 2.
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "invalid report input or arguments\n"
