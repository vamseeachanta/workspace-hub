"""Offline parity contract for issue #2765.

All timestamps and cron strings below are synthetic example inputs, not measured
schedules. Expected findings are hand-authored by matching the explicit identity
and surface pairs: absence gives missing, repeated pairs give duplicate, and
unequal schedule/runtime strings give separate mismatches. Counts are independent
hand counts of the example rows, never derived through the implementation.
"""
from __future__ import annotations

import copy
import importlib.util
import itertools
import json
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/analysis/scheduler_parity_report.py"
OBSERVED_AT = "2026-10-15T12:00:00Z"


def _load_module():
    spec = importlib.util.spec_from_file_location("scheduler_parity_report", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def report_module():
    return _load_module()


def job(logical_id="maintenance", surface="system-cron", schedule="0 3 * * *",
        runtime="deterministic"):
    return dict(logical_id=logical_id, surface=surface, schedule=schedule, runtime=runtime)


def snapshot(*jobs, available=True):
    return {"available": available, "jobs": list(jobs)}


def build(module, canonical, actuals):
    return module.build_report(canonical, actuals, observed_at=OBSERVED_AT)


def test_matching_snapshots_have_no_findings(report_module):
    canonical = snapshot(job(), job("digest", "gateway", runtime="agent"))
    original = copy.deepcopy(canonical)
    result = build(report_module, canonical, {
        "system-cron": snapshot(job()),
        "gateway": snapshot(job("digest", "gateway", runtime="agent")),
    })
    assert result == {
        "observed_at": OBSERVED_AT,
        "canonical_available": True,
        "surfaces": [
            {"surface": "gateway", "status": "known"},
            {"surface": "system-cron", "status": "known"},
        ],
        "findings": [],
    }
    assert canonical == original


def test_missing_task_has_stable_reason(report_module):
    assert build(report_module, snapshot(job()), {"system-cron": snapshot()})["findings"] == [
        {"kind": "missing", "reason": "absent_from_available_snapshot",
         "logical_id": "maintenance", "surface": "system-cron"},
    ]


def test_duplicate_schedule_and_runtime_mismatch_are_distinct(report_module):
    canonical = snapshot(job("duplicate"), job("schedule"), job("runtime"), job("both"))
    actual = snapshot(
        job("duplicate"), job("duplicate", schedule="0 4 * * *"),
        job("schedule", schedule="0 4 * * *"),
        job("runtime", runtime="agent"),
        job("both", schedule="0 4 * * *", runtime="agent"),
    )
    assert build(report_module, canonical, {"system-cron": actual})["findings"] == [
        {"kind": "runtime_mismatch", "reason": "runtime_class_differs",
         "logical_id": "both", "surface": "system-cron",
         "expected": "deterministic", "actual": "agent"},
        {"kind": "schedule_mismatch", "reason": "schedule_string_differs",
         "logical_id": "both", "surface": "system-cron",
         "expected": "0 3 * * *", "actual": "0 4 * * *"},
        {"kind": "duplicate", "reason": "repeated_identity_on_surface",
         "logical_id": "duplicate", "surface": "system-cron",
         "snapshot": "actual", "count": 2},
        {"kind": "runtime_mismatch", "reason": "runtime_class_differs",
         "logical_id": "runtime", "surface": "system-cron",
         "expected": "deterministic", "actual": "agent"},
        {"kind": "schedule_mismatch", "reason": "schedule_string_differs",
         "logical_id": "schedule", "surface": "system-cron",
         "expected": "0 3 * * *", "actual": "0 4 * * *"},
    ]


@pytest.mark.parametrize("actuals,reason", [
    ({}, "snapshot_missing"),
    ({"system-cron": None}, "snapshot_missing"),
    ({"system-cron": snapshot(available=False)}, "snapshot_unavailable"),
])
def test_missing_snapshot_is_unknown_not_empty(report_module, actuals, reason):
    result = build(report_module, snapshot(job()), actuals)
    assert result["findings"] == []
    assert result["surfaces"] == [
        {"surface": "system-cron", "status": "unknown", "reason": reason},
    ]


def test_input_order_does_not_change_report(report_module):
    canonical_rows = [job("a"), job("b"), job("a", "gateway")]
    actual_rows = [job("b", runtime="agent"), job("c"), job("c")]
    expected = build(report_module, snapshot(*canonical_rows), {
        "gateway": snapshot(), "system-cron": snapshot(*actual_rows),
    })
    expected_json = report_module.report_json(expected)
    for rows in itertools.permutations(canonical_rows):
        for actual in itertools.permutations(actual_rows):
            actuals = {"system-cron": snapshot(*actual), "gateway": snapshot()}
            result = build(report_module, snapshot(*rows), actuals)
            assert result == expected
            assert report_module.report_json(result) == expected_json
    assert json.loads(expected_json) == expected


def test_identity_includes_surface(report_module):
    result = build(report_module, snapshot(job(), job(surface="gateway")), {
        "system-cron": snapshot(job()), "gateway": snapshot(),
    })
    assert result["findings"] == [
        {"kind": "missing", "reason": "absent_from_available_snapshot",
         "logical_id": "maintenance", "surface": "gateway"},
    ]


def test_unexpected_mapped_job_is_reported(report_module):
    assert build(report_module, snapshot(), {"system-cron": snapshot(job())})["findings"] == [
        {"kind": "unexpected", "reason": "absent_from_canonical_snapshot",
         "logical_id": "maintenance", "surface": "system-cron"},
    ]


def test_duplicate_canonical_is_not_arbitrarily_compared(report_module):
    result = build(report_module, snapshot(job(), job(schedule="0 4 * * *")), {
        "system-cron": snapshot(job(runtime="agent")),
    })
    assert result["findings"] == [
        {"kind": "duplicate", "reason": "repeated_identity_on_surface",
         "logical_id": "maintenance", "surface": "system-cron",
         "snapshot": "canonical", "count": 2},
    ]


def test_unavailable_canonical_does_not_mark_actual_jobs_unexpected(report_module):
    result = build(report_module, snapshot(available=False), {"system-cron": snapshot(job())})
    assert result["canonical_available"] is False
    assert result["findings"] == []
    assert result["surfaces"] == [
        {"surface": "system-cron", "status": "unknown", "reason": "canonical_unavailable"},
    ]


@pytest.mark.parametrize("logical_id", [None, "", " ", 7])
def test_reject_unmapped_identity(report_module, logical_id):
    record = job(logical_id=logical_id)
    with pytest.raises(ValueError, match="logical_id"):
        build(report_module, snapshot(job()), {"system-cron": snapshot(record)})


def test_command_text_is_not_an_identity_mapping(report_module):
    record = job()
    del record["logical_id"]
    record["command"] = "echo maintenance"
    with pytest.raises(ValueError, match="logical_id"):
        build(report_module, snapshot(job()), {"system-cron": snapshot(record)})


@pytest.mark.parametrize("bad", [
    {}, {"available": "false", "jobs": []}, {"available": True, "jobs": {}},
    snapshot(job(), available=False), snapshot({**job(), "command": "echo maintenance"}),
    snapshot(job(schedule="")), snapshot(job(runtime=None)), snapshot(job(surface="")),
    {"available": True, "jobs": [], "extra": True},
])
def test_reject_malformed_snapshots(report_module, bad):
    with pytest.raises(ValueError):
        build(report_module, bad, {"system-cron": snapshot()})


def test_reject_record_from_wrong_surface(report_module):
    with pytest.raises(ValueError, match="surface"):
        build(report_module, snapshot(job()), {"system-cron": snapshot(job(surface="gateway"))})


@pytest.mark.parametrize("observed_at", [None, "", "2026-10-15", "2026-10-15T12:00:00",
                                       "2026-02-30T12:00:00Z"])
def test_observation_time_must_be_explicit_and_zoned(report_module, observed_at):
    with pytest.raises(ValueError, match="observed_at"):
        report_module.build_report(snapshot(), {}, observed_at=observed_at)


def test_schedule_strings_are_compared_verbatim(report_module):
    result = build(report_module, snapshot(job()), {
        "system-cron": snapshot(job(schedule="0  3 * * *")),
    })
    assert result["findings"] == [
        {"kind": "schedule_mismatch", "reason": "schedule_string_differs",
         "logical_id": "maintenance", "surface": "system-cron",
         "expected": "0 3 * * *", "actual": "0  3 * * *"},
    ]


@pytest.fixture
def forbid_collection(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("subprocess or network collection attempted")
    for name in ("Popen", "run", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, forbidden)
    for name in ("socket", "create_connection", "getaddrinfo"):
        monkeypatch.setattr(socket, name, forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)


def test_import_api_and_cli_do_not_collect(forbid_collection, tmp_path, capsys):
    report_module = _load_module()
    canonical = tmp_path / "canonical.json"
    actual = tmp_path / "actual.json"
    canonical.write_text(json.dumps(snapshot(job())), encoding="utf-8")
    actual.write_text(json.dumps(snapshot(job())), encoding="utf-8")
    expected = build(report_module, snapshot(job()), {"system-cron": snapshot(job())})
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert report_module.main([
        "--canonical", str(canonical), "--actual", f"system-cron={actual}",
        "--observed-at", OBSERVED_AT,
    ]) == 0
    assert capsys.readouterr().out == report_module.report_json(expected) + "\n"
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_cli_missing_actual_file_is_unknown(report_module, tmp_path, capsys):
    canonical = tmp_path / "canonical.json"
    canonical.write_text(json.dumps(snapshot(job())), encoding="utf-8")
    assert report_module.main([
        "--canonical", str(canonical), "--actual", f"system-cron={tmp_path / 'absent.json'}",
        "--observed-at", OBSERVED_AT,
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["findings"] == []
    assert result["surfaces"] == [
        {"surface": "system-cron", "status": "unknown", "reason": "snapshot_missing"},
    ]


@pytest.mark.parametrize("raw", [
    '{"available":true,"available":false,"jobs":[]}',
    '{"available":true,"jobs":[],"invalid":NaN}',
    '{"available":true,"jobs":[],"invalid":Infinity}',
    '{broken',
])
def test_cli_rejects_invalid_json_without_partial_report(report_module, tmp_path, capsys, raw):
    canonical = tmp_path / "canonical.json"
    canonical.write_text(raw, encoding="utf-8")
    assert report_module.main(["--canonical", str(canonical), "--observed-at", OBSERVED_AT]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert str(tmp_path) not in captured.err


def test_cli_rejects_repeated_actual_surface(report_module, tmp_path, capsys):
    canonical = tmp_path / "canonical.json"
    canonical.write_text(json.dumps(snapshot()), encoding="utf-8")
    assert report_module.main([
        "--canonical", str(canonical), "--actual", f"system-cron={canonical}",
        "--actual", f"system-cron={canonical}", "--observed-at", OBSERVED_AT,
    ]) == 2
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("observed_at", [
    "2026-10-15T12:00:00+00:60", "2026-10-15T12:00:00+01:99",
    "2026-10-15T12:00:00-00:00",
])
def test_reject_unknown_or_invalid_timezone_offsets(report_module, observed_at):
    with pytest.raises(ValueError, match="observed_at"):
        report_module.build_report(snapshot(), {}, observed_at=observed_at)


@pytest.mark.parametrize("raw", ["null", "[]", "true", "7", '"snapshot"'])
def test_cli_rejects_nonobject_actual_json(report_module, tmp_path, capsys, raw):
    canonical = tmp_path / "canonical.json"
    actual = tmp_path / "actual.json"
    canonical.write_text(json.dumps(snapshot(job())), encoding="utf-8")
    actual.write_text(raw, encoding="utf-8")
    assert report_module.main([
        "--canonical", str(canonical), "--actual", f"system-cron={actual}",
        "--observed-at", OBSERVED_AT,
    ]) == 2
    assert capsys.readouterr().out == ""
