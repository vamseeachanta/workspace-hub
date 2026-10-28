"""Synthetic recurrence evidence for issue #2197; no operational audit records.

Hand calculation (each cell is presence after within-run deduplication):
                         week-a  week-b  week-c  week-d | total  final streak
provider-a / docs/a.md       yes     yes      no     yes |     3             1
provider-a / docs/b.md       yes     yes     yes     yes |     4             4
provider-a / docs/gone.md    yes      no      no      no |     1             0
provider-b / docs/a.md        no     yes     yes     yes |     3             3

All dates, multiplicities and expected counts below are synthetic, calculated
from this table or the explicitly stated smaller examples, not policy limits.
"""

from copy import deepcopy
from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys

import pytest

from unresolved_read_cohorts import reduce_snapshots


def observation(target="docs/a.md", provider="provider-a"):
    return {"provider": provider, "canonical_target": target}


@pytest.fixture
def weekly_snapshots():
    # Hand-selected weekly dates; repeated a.md entries are one presence per run.
    return [
        {"run_id": "week-a", "generated_at": "2026-01-05T00:00:00Z",
         "observations": [observation(), observation(), observation("docs/b.md"),
                          observation("docs/gone.md")]},
        {"run_id": "week-b", "generated_at": "2026-01-12T00:00:00Z",
         "observations": [observation(), observation("docs/b.md"),
                          observation(provider="provider-b")]},
        {"run_id": "week-c", "generated_at": "2026-01-19T00:00:00Z",
         "observations": [observation("docs/b.md"), observation(provider="provider-b")]},
        {"run_id": "week-d", "generated_at": "2026-01-26T00:00:00Z",
         "observations": [observation(), observation("docs/b.md"),
                          observation(provider="provider-b"), observation(provider="provider-b")]},
    ]


@pytest.fixture
def expected_cohorts():
    """Literal results calculated from the presence table above."""
    return [
        {"provider": "provider-a", "canonical_target": "docs/a.md",
         "total_observations": 3, "consecutive_runs": 1,
         "first_seen": "2026-01-05T00:00:00+00:00", "last_seen": "2026-01-26T00:00:00+00:00"},
        {"provider": "provider-a", "canonical_target": "docs/b.md",
         "total_observations": 4, "consecutive_runs": 4,
         "first_seen": "2026-01-05T00:00:00+00:00", "last_seen": "2026-01-26T00:00:00+00:00"},
        {"provider": "provider-a", "canonical_target": "docs/gone.md",
         "total_observations": 1, "consecutive_runs": 0,
         "first_seen": "2026-01-05T00:00:00+00:00", "last_seen": "2026-01-05T00:00:00+00:00"},
        {"provider": "provider-b", "canonical_target": "docs/a.md",
         "total_observations": 3, "consecutive_runs": 3,
         "first_seen": "2026-01-12T00:00:00+00:00", "last_seen": "2026-01-26T00:00:00+00:00"},
    ]


def test_consecutive_and_total_counts_differ(weekly_snapshots, expected_cohorts):
    assert reduce_snapshots(weekly_snapshots) == expected_cohorts


def test_return_after_gap_resets_streak(weekly_snapshots):
    # a.md is present twice, absent once, then returns: streaks 2, 0, 1.
    before_gap = reduce_snapshots(weekly_snapshots[:2])[0]
    absent = reduce_snapshots(weekly_snapshots[:3])[0]
    returned = reduce_snapshots(weekly_snapshots)[0]
    assert (before_gap["consecutive_runs"], absent["consecutive_runs"], returned["consecutive_runs"]) == (2, 0, 1)
    assert returned["total_observations"] == 3
    assert returned["first_seen"] == before_gap["first_seen"]


def test_run_order_does_not_change_result(weekly_snapshots, expected_cohorts):
    expected = json.dumps(expected_cohorts)
    for ordering in permutations(weekly_snapshots):
        shuffled = deepcopy(list(ordering))
        for snapshot in shuffled:
            snapshot["observations"].reverse()
        assert json.dumps(reduce_snapshots(shuffled)) == expected


def test_duplicate_runs_and_observations_are_idempotent(weekly_snapshots, expected_cohorts):
    duplicate = deepcopy(weekly_snapshots[0])
    duplicate["observations"] = list(reversed(duplicate["observations"])) + [observation()]
    duplicate["generated_at"] = "2026-01-04T19:00:00-05:00"
    assert reduce_snapshots(weekly_snapshots + [duplicate]) == expected_cohorts


@pytest.mark.parametrize("change", [
    {"generated_at": "2026-01-06T00:00:00Z"},
    {"observations": []},
    {"observations": [observation(provider="provider-b")]},
])
def test_conflicting_duplicate_run_identity_is_rejected(weekly_snapshots, change):
    duplicate = dict(weekly_snapshots[0], **change)
    with pytest.raises(ValueError, match="conflicting run identity"):
        reduce_snapshots(weekly_snapshots + [duplicate])


def test_empty_run_breaks_streak_but_not_history(weekly_snapshots):
    empty = {"run_id": "week-e", "generated_at": "2026-02-02T00:00:00Z", "observations": []}
    rows = reduce_snapshots(weekly_snapshots + [empty])
    assert all(row["consecutive_runs"] == 0 for row in rows)
    assert [row["total_observations"] for row in rows] == [3, 4, 1, 3]
    assert rows[0]["last_seen"] == "2026-01-26T00:00:00+00:00"


def test_empty_input_has_no_cohorts():
    assert reduce_snapshots([]) == []


def test_input_is_not_mutated(weekly_snapshots):
    original = deepcopy(weekly_snapshots)
    result = reduce_snapshots(weekly_snapshots)
    result[0]["provider"] = "changed"
    assert weekly_snapshots == original


def test_chronology_uses_instants_and_run_identity_tiebreak():
    # First two instants are equal: a sorts before b. Third is one hour later,
    # despite its local date looking earlier. Presence yes/no/yes => total 2,
    # trailing streak 1, with the first and last instants expressed in UTC.
    snapshots = [
        {"run_id": "b", "generated_at": "2026-01-05T01:00:00+01:00", "observations": []},
        {"run_id": "c", "generated_at": "2026-01-04T20:00:00-05:00", "observations": [observation()]},
        {"run_id": "a", "generated_at": "2026-01-05T00:00:00Z", "observations": [observation()]},
    ]
    row, = reduce_snapshots(snapshots)
    assert (row["total_observations"], row["consecutive_runs"]) == (2, 1)
    assert row["first_seen"] == "2026-01-05T00:00:00+00:00"
    assert row["last_seen"] == "2026-01-05T01:00:00+00:00"


@pytest.mark.parametrize("field,value", [
    ("run_id", ""), ("run_id", None), ("run_id", 1), ("run_id", " padded "),
    ("generated_at", "2026-01-05"), ("generated_at", "2026-01-05T00:00:00"),
    ("generated_at", "invalid"), ("generated_at", None),
    ("observations", None), ("observations", {}), ("observations", [None]),
    ("observations", [{}]),
    ("observations", [{"provider": "", "canonical_target": "docs/a.md"}]),
    ("observations", [{"provider": "provider-a", "canonical_target": " "}]),
    ("observations", [{"provider": "provider-a", "canonical_target": False}]),
])
def test_invalid_snapshot_is_rejected(weekly_snapshots, field, value):
    snapshot = dict(weekly_snapshots[0], **{field: value})
    with pytest.raises(ValueError):
        reduce_snapshots([snapshot])


@pytest.mark.parametrize("snapshots", [None, {}, "snapshots", [None], [{}]])
def test_invalid_container_is_rejected(snapshots):
    with pytest.raises(ValueError):
        reduce_snapshots(snapshots)


def test_unknown_fields_are_rejected(weekly_snapshots):
    # Strict shape prevents silently ignoring conflicting duplicate contents.
    with pytest.raises(ValueError):
        reduce_snapshots([dict(weekly_snapshots[0], extra="unconsumed")])
    snapshot = deepcopy(weekly_snapshots[0])
    snapshot["observations"][0]["extra"] = "unconsumed"
    with pytest.raises(ValueError):
        reduce_snapshots([snapshot])


def test_canonical_identity_is_preserved_exactly(weekly_snapshots):
    # Canonicalization belongs upstream: case-distinct keys remain two cohorts.
    snapshot = dict(weekly_snapshots[0], observations=[observation("docs/A.md"), observation()])
    assert [row["canonical_target"] for row in reduce_snapshots([snapshot])] == ["docs/A.md", "docs/a.md"]


def test_cli_emits_only_json_and_writes_no_files(weekly_snapshots, expected_cohorts, tmp_path):
    script = Path(__file__).resolve().parents[2] / "scripts/reporting/unresolved_read_cohorts.py"
    result = subprocess.run([sys.executable, str(script)], input=json.dumps(weekly_snapshots),
                            text=True, capture_output=True, cwd=tmp_path, check=False)
    assert result.returncode == 0
    assert json.loads(result.stdout) == expected_cohorts
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("payload", ["invalid JSON", "{}", '[{"run_id":"bad"}]'])
def test_cli_errors_are_json_without_input_echo(payload, tmp_path):
    script = Path(__file__).resolve().parents[2] / "scripts/reporting/unresolved_read_cohorts.py"
    result = subprocess.run([sys.executable, str(script)], input=payload,
                            text=True, capture_output=True, cwd=tmp_path, check=False)
    assert result.returncode != 0
    assert result.stdout == ""
    assert isinstance(json.loads(result.stderr)["error"], str)
    assert payload not in result.stderr
    assert list(tmp_path.iterdir()) == []
