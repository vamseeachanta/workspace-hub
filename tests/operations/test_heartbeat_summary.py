"""Synthetic examples and independent time arithmetic for heartbeat summaries.

All dates are invented. At noon UTC, 11:55 is five minutes earlier and 11:30
is thirty minutes earlier. These hand subtractions define the thresholds below;
no expected value is derived using the implementation. No fixture uses live data.
"""

from copy import deepcopy
from datetime import timedelta
import importlib.util
from pathlib import Path

import pytest


# The second ancestor is the repository root by this test directory's layout.
MODULE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts/operations/heartbeat_summary.py"
)
SPEC = importlib.util.spec_from_file_location("heartbeat_summary", MODULE_PATH)
heartbeat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(heartbeat)

AS_OF = "2026-10-15T12:00:00Z"
# Hand calculation: noon minus 11:55 = 5 minutes; noon minus 11:30 = 30 minutes.
FRESHNESS = timedelta(minutes=5)
OFFLINE = timedelta(minutes=30)


def record(timestamp, role="worker"):
    return {"role": role, "observed_at": timestamp}


def summarize(records, role="worker", **options):
    return heartbeat.summarize_heartbeats(
        role,
        records,
        as_of=options.get("as_of", AS_OF),
        freshness=options.get("freshness", FRESHNESS),
        offline_after=options.get("offline_after", OFFLINE),
    )


@pytest.mark.parametrize(
    "timestamp, state, reason",
    [
        # Hand elapsed times: 0, 4:59, 5:00, 5:01, 29:59, 30:00, 30:01.
        ("2026-10-15T12:00:00Z", "fresh", "within_freshness"),
        ("2026-10-15T11:55:01Z", "fresh", "within_freshness"),
        ("2026-10-15T11:55:00Z", "fresh", "within_freshness"),
        ("2026-10-15T11:54:59Z", "stale", "freshness_exceeded"),
        ("2026-10-15T11:30:01Z", "stale", "freshness_exceeded"),
        ("2026-10-15T11:30:00Z", "offline", "offline_threshold_reached"),
        ("2026-10-15T11:29:59Z", "offline", "offline_threshold_reached"),
    ],
)
def test_freshness_boundary_table(timestamp, state, reason):
    assert summarize([record(timestamp)]) == {
        "role": "worker",
        "last_seen": timestamp.replace("Z", "+00:00"),
        "state": state,
        "reason_codes": [reason],
    }


@pytest.mark.parametrize(
    "records, reasons",
    [
        ([], ["missing_evidence"]),
        ([record("2026-10-15T12:00:01Z")], ["future_evidence"]),
        ([record("2026-10-15T11:59:00Z", "reviewer")], ["missing_evidence"]),
    ],
)
def test_missing_and_future_evidence_unverified(records, reasons):
    # Noon minus 12:00:01 is negative one second, hence not usable evidence.
    result = summarize(records)
    assert result["state"] == "unverified"
    assert result["last_seen"] is None
    assert result["reason_codes"] == reasons


def test_latest_valid_record_selected():
    # Noon minus 11:56 = 4 minutes; minus 11:40 = 20 minutes. Order is irrelevant.
    records = [
        record("2026-10-15T11:40:00Z"),
        record("2026-10-15T11:56:00Z"),
        record("2026-10-15T11:59:00Z", "reviewer"),
        record("2026-10-15T11:50:00Z"),
    ]
    expected = {
        "role": "worker",
        "last_seen": "2026-10-15T11:56:00+00:00",
        "state": "fresh",
        "reason_codes": ["within_freshness"],
    }
    assert summarize(records) == expected
    assert summarize(list(reversed(records))) == expected


@pytest.mark.parametrize(
    "timestamp",
    ["2026-10-15T13:55:00+02:00", "2026-10-15T04:55:00-07:00"],
)
def test_timezone_equivalent_instants(timestamp):
    # 13:55 minus 2 hours and 04:55 plus 7 hours both equal 11:55 UTC.
    assert summarize([record(timestamp)]) == summarize([record("2026-10-15T11:55:00Z")])
    assert summarize([record(timestamp)], as_of="2026-10-15T14:00:00+02:00") == summarize(
        [record("2026-10-15T11:55:00Z")]
    )


@pytest.mark.parametrize(
    "evidence",
    [
        None,
        [],
        "not a record",
        {},
        {"role": "worker"},
        {"observed_at": AS_OF},
        record(None),
        record(True),
        record("invalid"),
        record("2026-02-30T11:55:00Z"),  # Invented impossible calendar date.
        record("2026-10-15T11:55:00"),  # Missing offset.
        record("2026-10-15"),
        record("20261015T115500Z"),  # Basic ISO form is outside the contract.
        record("2026-10-15X11:55:00Z"),
        record("2026-10-15T11:55:00-00:00"),  # Unknown local offset.
        {**record(AS_OF), "metadata": "unexpected"},
    ],
)
def test_malformed_evidence_unverified(evidence):
    result = summarize([evidence])
    assert result["state"] == "unverified"
    assert result["last_seen"] is None
    assert result["reason_codes"] == ["malformed_evidence"]


@pytest.mark.parametrize("role", ["unknown", " worker", "WORKER", None, []])
def test_unknown_requested_role_is_not_echoed(role):
    assert summarize([record(AS_OF)], role=role) == {
        "role": None,
        "last_seen": None,
        "state": "unverified",
        "reason_codes": ["unknown_role"],
    }


@pytest.mark.parametrize("role", ["unknown", " worker", "WORKER", None, []])
def test_unknown_evidence_role_unverified(role):
    result = summarize([record(AS_OF, role)])
    assert result["state"] == "unverified"
    assert result["last_seen"] is None
    assert result["reason_codes"] == ["unknown_role"]


def test_invalid_records_preserve_last_seen_without_claiming_freshness():
    # Noon minus 11:56 = 4 minutes; future evidence cannot supersede that instant.
    valid = record("2026-10-15T11:56:00Z")
    records = [valid, record("2026-10-15T12:00:01Z"), {}, record(AS_OF, "unknown")]
    result = summarize(records)
    assert result["last_seen"] == "2026-10-15T11:56:00+00:00"
    assert result["state"] == "unverified"
    assert result["reason_codes"] == [
        "future_evidence", "malformed_evidence", "unknown_role"
    ]
    assert summarize(list(reversed(records))) == result


@pytest.mark.parametrize("role", ["worker", "reviewer", "controller"])
def test_supported_roles_are_logical_not_discovered_inventory(role):
    result = summarize([record(AS_OF, role)], role=role)
    assert result["role"] == role
    assert result["state"] == "fresh"


@pytest.mark.parametrize("records", [None, {}, "not records", True])
def test_malformed_record_collection(records):
    assert summarize(records)["reason_codes"] == ["malformed_evidence"]


@pytest.mark.parametrize("as_of", [None, AS_OF[:-1], "invalid", "2026-10-15"])
def test_invalid_as_of_is_caller_error(as_of):
    with pytest.raises(ValueError, match="as_of"):
        summarize([], as_of=as_of)


@pytest.mark.parametrize(
    "freshness, offline_after",
    [
        # Negative duration, reversed thresholds, and equal thresholds are invalid.
        (timedelta(seconds=-1), OFFLINE),
        (OFFLINE, FRESHNESS),
        (FRESHNESS, FRESHNESS),
        (FRESHNESS, timedelta()),
        (None, OFFLINE),
        (FRESHNESS, "invalid"),
    ],
)
def test_invalid_thresholds_are_caller_errors(freshness, offline_after):
    with pytest.raises(ValueError, match="duration"):
        summarize([], freshness=freshness, offline_after=offline_after)


def test_caller_thresholds_and_subsecond_boundaries():
    # Noon minus 11:59:59.5 = half a second; minus 11:59:59 = one second.
    # With zero freshness and one-second offline, these are stale and offline.
    options = {"freshness": timedelta(), "offline_after": timedelta(seconds=1)}
    assert summarize([record("2026-10-15T12:00:00Z")], **options)["state"] == "fresh"
    assert summarize([record("2026-10-15T11:59:59.500000Z")], **options)["state"] == "stale"
    assert summarize([record("2026-10-15T11:59:59Z")], **options)["state"] == "offline"


def test_preserves_caller_files_metadata_and_input(tmp_path):
    # Synthetic file is a sentinel: the summarizer receives only in-memory records.
    sentinel = tmp_path / "caller.txt"
    sentinel.write_text("preserve this synthetic input", encoding="utf-8")
    before_bytes = sentinel.read_bytes()
    before_stat = sentinel.stat()
    before_entries = set(tmp_path.iterdir())
    records = [record("2026-10-15T11:55:00Z")]
    before_records = deepcopy(records)
    summarize(records)
    assert records == before_records
    assert sentinel.read_bytes() == before_bytes
    after_stat = sentinel.stat()
    assert (after_stat.st_mtime_ns, after_stat.st_mode, after_stat.st_size) == (
        before_stat.st_mtime_ns, before_stat.st_mode, before_stat.st_size
    )
    assert set(tmp_path.iterdir()) == before_entries


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-10-15T11:55:00+00:60",  # Offset minutes must be below sixty.
        "2026-10-15T11:55:00-00:60",
        "2026-10-15T11:55:00+24:00",  # Offset hours must be below twenty-four.
        "0001-01-01T00:00:00+01:00",  # UTC conversion precedes representable dates.
    ],
)
def test_invalid_or_unrepresentable_offset_is_unverified(timestamp):
    assert summarize([record(timestamp)])["reason_codes"] == ["malformed_evidence"]


def test_previous_day_and_duplicate_observations():
    # Midnight minus 23:55 on the prior day is five minutes, exactly fresh.
    observation = record("2026-10-14T23:55:00Z")
    assert summarize(
        (observation, observation), as_of="2026-10-15T00:00:00Z"
    ) == {
        "role": "worker",
        "last_seen": "2026-10-14T23:55:00+00:00",
        "state": "fresh",
        "reason_codes": ["within_freshness"],
    }


def test_bad_unattributable_evidence_cannot_be_silently_ignored():
    # A future observation for another role still invalidates the shared collection.
    result = summarize([record(AS_OF), record("2026-10-15T12:00:01Z", "reviewer")])
    assert result["state"] == "unverified"
    assert result["last_seen"] == "2026-10-15T12:00:00+00:00"
    assert result["reason_codes"] == ["future_evidence"]
