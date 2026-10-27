"""Synthetic evidence-reader examples for issue #3087; no live quota discovery.

Fixture basis (hand-authored, not measured usage): the clock is fixed at noon
UTC on 2026-01-15, and snapshots are captured at 10:00 that day. Their age is
therefore two hours, below the explicitly configured 48-hour freshness limit.
Window examples use 20% and 70% remaining, or a 35% tie; the lower percentage
binds and ties prefer weekly, as required by the issue's evidence-reader scope.
Nested reset examples are 30 hours (weekly) and 4 hours (five-hour); legacy
examples carry no reset duration. These are fixture values, not quota caps.

The throttle table below cites its own instants and independently calculates
reset times relative to noon. Percent zero means exhausted. A successful main
returns zero and emits exactly one JSON line, per the helper's output contract.
Numeric filenames in that table encode the explicit UTC error instants; they
are synthetic files beneath pytest's temporary directory.
"""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Two parent levels reach the repository root from tests/ai/.
HELPER = Path(__file__).resolve().parents[2] / "scripts/ai/assessment/gemini-usage.py"
NOW = datetime.fromisoformat("2026-01-15T12:00:00+00:00")
CAPTURED_AT = "2026-01-15T10:00:00Z"
UNAVAILABLE = {
    "pct_remaining": None,
    "hours_to_reset": None,
    "window": None,
    "captured_at": None,
    "stale": False,
    "source": "unavailable",
}


@pytest.fixture
def reader(tmp_path, monkeypatch):
    snapshot = tmp_path / "snapshot.json"
    errors = tmp_path / "errors"
    errors.mkdir()
    # Configure before import so inherited settings cannot select actual logs.
    monkeypatch.setenv("AGY_USAGE_SNAPSHOT", str(snapshot))
    monkeypatch.setenv("GEMINI_ERROR_DIR", str(errors))
    monkeypatch.setenv("STATUSLINE_GEMINI_SNAPSHOT_MAX_AGE_HOURS", "48")
    spec = importlib.util.spec_from_file_location("gemini_usage_under_test", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz or timezone.utc)

    monkeypatch.setattr(module, "datetime", FixedDatetime)
    return module, snapshot, errors


def read_result(reader, capsys):
    module, _, _ = reader
    assert module.main() == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    lines = captured.out.splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


def write_snapshot(path, windows):
    path.write_text(
        json.dumps({"captured_at": CAPTURED_AT, "gemini": windows}),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "weekly,five_hour,window,remaining,reset",
    [
        pytest.param(20, 70, "weekly", 20, 30, id="weekly-binds"),
        pytest.param(70, 20, "five_hour", 20, 4, id="five-hour-binds"),
        pytest.param(35, 35, "weekly", 35, 30, id="weekly-wins-tie"),
    ],
)
def test_nested_binding_window(reader, capsys, weekly, five_hour, window, remaining, reset):
    _, snapshot, _ = reader
    # Put five_hour first so the tie case cannot pass by insertion order alone.
    write_snapshot(snapshot, {
        "five_hour": {"pct_remaining": five_hour, "reset_hours": 4},
        "weekly": {"pct_remaining": weekly, "reset_hours": 30},
    })
    assert read_result(reader, capsys) == {
        "pct_remaining": remaining,
        "hours_to_reset": reset,
        "window": window,
        "captured_at": CAPTURED_AT,
        "stale": False,
        "source": "manual-snapshot",
    }


@pytest.mark.parametrize(
    "weekly,five_hour,window,remaining",
    [
        pytest.param(20, 70, "weekly", 20, id="weekly-binds"),
        pytest.param(70, 20, "five_hour", 20, id="five-hour-binds"),
        pytest.param(35, 35, "weekly", 35, id="weekly-wins-tie"),
    ],
)
def test_legacy_flat_binding_window(reader, capsys, weekly, five_hour, window, remaining):
    _, snapshot, _ = reader
    write_snapshot(snapshot, {
        "weekly_pct_avail": weekly,
        "five_hour_pct_avail": five_hour,
    })
    assert read_result(reader, capsys) == {
        "pct_remaining": remaining,
        "hours_to_reset": None,
        "window": window,
        "captured_at": CAPTURED_AT,
        "stale": False,
        "source": "manual-snapshot",
    }


@pytest.mark.parametrize("contents", [None, '{"gemini":'], ids=["absent", "invalid-json"])
def test_missing_evidence_is_unavailable(reader, capsys, contents):
    _, snapshot, _ = reader
    if contents is not None:
        snapshot.write_text(contents, encoding="utf-8")
    assert read_result(reader, capsys) == UNAVAILABLE


# Independent timeline basis: capture 10:00, now 12:00, all on 2026-01-15 UTC.
# 09:00 + 4h = 13:00: active but older than capture, so retain snapshot.
# 10:00 + 3h = 13:00: active but equal to capture, so retain snapshot.
# 10:30 + 1h30m = 12:00: expires exactly now, so retain snapshot.
# 11:00 + 30m = 11:30: newer but expired, so retain snapshot.
# 11:00 + 2h17m30s = 13:17:30: 77.5 minutes left, rounded to 1.3 hours.
# 11:30 + 1h24m = 12:54: 54 minutes left, or 0.9 hours; newest active wins.
OLDER = ("2026-01-15T09-00-00-000Z", "4h")
SAME_TIME = ("2026-01-15T10-00-00-000Z", "3h")
EXPIRES_NOW = ("2026-01-15T10-30-00-000Z", "1h30m")
EXPIRED = ("2026-01-15T11-00-00-000Z", "30m")
NEWER = ("2026-01-15T11-00-00-000Z", "2h17m30s")
NEWEST = ("2026-01-15T11-30-00-000Z", "1h24m")


@pytest.mark.parametrize(
    "events,has_snapshot,remaining,reset,window,source",
    [
        pytest.param([NEWER], True, 0, 1.3, "five_hour", "429-throttle", id="newer-active"),
        pytest.param([EXPIRED], True, 20, 30, "weekly", "manual-snapshot", id="expired"),
        pytest.param([OLDER], True, 20, 30, "weekly", "manual-snapshot", id="older-active"),
        pytest.param([SAME_TIME], True, 20, 30, "weekly", "manual-snapshot", id="equal-time"),
        pytest.param([EXPIRES_NOW], True, 20, 30, "weekly", "manual-snapshot", id="reset-now"),
        pytest.param([NEWEST, NEWER, OLDER], True, 0, 0.9, "five_hour", "429-throttle",
                     id="latest-active-regardless-of-file-order"),
        pytest.param([EXPIRED, OLDER], True, 20, 30, "weekly", "manual-snapshot",
                     id="expired-newer-does-not-revive-older"),
        pytest.param([NEWER], False, 0, 1.3, "five_hour", "429-throttle",
                     id="active-without-snapshot"),
    ],
)
def test_throttle_timeline(reader, capsys, events, has_snapshot, remaining, reset, window, source):
    _, snapshot, errors = reader
    if has_snapshot:
        write_snapshot(snapshot, {
            "weekly": {"pct_remaining": 20, "reset_hours": 30},
            "five_hour": {"pct_remaining": 70, "reset_hours": 4},
        })
    for instant, duration in events:
        (errors / f"gemini-client-error-{instant}.json").write_text(
            json.dumps({"error": {"message": f"quota exhausted; reset after {duration}"}}),
            encoding="utf-8",
        )
    assert read_result(reader, capsys) == {
        "pct_remaining": remaining,
        "hours_to_reset": reset,
        "window": window,
        "captured_at": CAPTURED_AT if source == "manual-snapshot" else None,
        "stale": False,
        "source": source,
    }
