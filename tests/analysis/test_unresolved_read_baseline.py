"""Synthetic examples; expected results are calculated independently beside cases."""

from __future__ import annotations

import builtins
from copy import deepcopy
import importlib.util
from itertools import permutations
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/analysis/unresolved_read_baseline.py"
spec = importlib.util.spec_from_file_location("unresolved_read_baseline", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def observation(raw=12, canonical=3, *, run_id="sample-a", provider="provider-a"):
    # Synthetic default: 12 - 3 = 9 fewer reads; 9 / 12 * 100 = 75.0 percent.
    return {
        "run_id": run_id,
        "provider": provider,
        "raw_unresolved": raw,
        "canonical_unresolved": canonical,
    }


def test_hand_calculated_reduction():
    # Independent calculation: 12 - 3 = 9; 9 / 12 * 100 = 75.0 percent.
    assert module.build_baseline([observation()]) == [{
        **observation(),
        "delta": 9,
        "percent_reduction": 75.0,
        "canonical_exceeds_raw": False,
        "budget": None,
        "budget_status": "not_configured",
    }]


@pytest.mark.parametrize("canonical", [0, 3])
def test_zero_raw_is_not_applicable(canonical):
    # Neither 0 / 0 nor -3 / 0 defines a percent reduction.
    row = module.build_baseline([observation(0, canonical)])[0]
    assert row["percent_reduction"] is None
    assert row["delta"] == -canonical
    assert row["canonical_exceeds_raw"] is (canonical > 0)


def test_canonical_exceeds_raw():
    # 4 - 6 = -2; -2 / 4 * 100 = -50.0 percent, retaining the anomaly.
    row = module.build_baseline([observation(4, 6)])[0]
    assert row["delta"] == -2
    assert row["percent_reduction"] == -50.0
    assert row["canonical_exceeds_raw"] is True


@pytest.mark.parametrize("canonical,status", [(2, "within"), (3, "within"), (4, "exceeded")])
def test_supplied_budget_boundary(canonical, status):
    # Synthetic maximum is 3 canonical reads: 2 <= 3, 3 <= 3, 4 > 3.
    row = module.build_baseline(
        [observation(12, canonical)], budgets={"provider-a": 3}
    )[0]
    assert row["budget"] == 3
    assert row["budget_status"] == status


def test_budget_zero_and_unconfigured_provider():
    # Explicit zero allows zero reads; absence supplies no inferred limit.
    rows = module.build_baseline(
        [observation(0, 0), observation(provider="provider-b")],
        budgets={"provider-a": 0},
    )
    assert [(r["budget"], r["budget_status"]) for r in rows] == [
        (0, "within"), (None, "not_configured")
    ]


@pytest.mark.parametrize("raw,canonical,percent", [
    (3, 2, 33.3),  # (3 - 2) / 3 * 100 = 100 / 3, rounded to one decimal.
    (16, 15, 6.2),  # 100 / 16 = 6.25; ties round to the even tenth.
    (16, 13, 18.8),  # 300 / 16 = 18.75; ties round to the even tenth.
    (5, 5, 0.0),  # No reduction: (5 - 5) / 5 = 0.
    (5, 0, 100.0),  # Complete reduction: (5 - 0) / 5 = 1.
])
def test_one_decimal_percent(raw, canonical, percent):
    row = module.build_baseline([observation(raw, canonical)])[0]
    assert row["percent_reduction"] == percent


def test_input_permutations_aggregate_deterministically():
    # For sample-a/provider-a: raw = 12 + 4 = 16, canonical = 3 + 1 = 4;
    # delta = 12 and percent = 12 / 16 * 100 = 75.0. Other keys stay separate.
    inputs = [observation(), observation(4, 1),
              observation(8, 4, provider="provider-b"),
              observation(10, 2, run_id="sample-b")]
    expected = [
        ("sample-a", "provider-a", 16, 4, 12, 75.0, 4, "within"),
        ("sample-a", "provider-b", 8, 4, 4, 50.0, None, "not_configured"),
        ("sample-b", "provider-a", 10, 2, 8, 80.0, 4, "within"),
    ]
    for ordering in permutations(inputs):
        rows = module.build_baseline(iter(ordering), budgets={"provider-a": 4})
        assert all(r["canonical_exceeds_raw"] is False for r in rows)
        assert [tuple(r[k] for k in (
            "run_id", "provider", "raw_unresolved", "canonical_unresolved",
            "delta", "percent_reduction", "budget", "budget_status",
        )) for r in rows] == expected


def test_history_appends_without_mutating_or_recalibrating():
    # Old budget 3 remains recorded even when the caller later supplies 1.
    history = module.build_baseline([observation()], budgets={"provider-a": 3})
    history[0]["metadata"] = {"tags": ["synthetic"]}
    original = deepcopy(history)
    inputs = [observation(4, 1, run_id="sample-b")]
    original_inputs = deepcopy(inputs)
    budgets = {"provider-a": 1}
    result = module.build_baseline(inputs, history=history, budgets=budgets)
    assert result[:-1] == original
    assert result[-1]["budget"] == 1
    assert history == original
    assert inputs == original_inputs
    assert budgets == {"provider-a": 1}
    result[0]["metadata"]["tags"].append("copy-only")
    result[-1]["raw_unresolved"] = 0
    assert history == original
    assert inputs == original_inputs


def test_history_preserves_order_even_with_earlier_sort_key():
    history = module.build_baseline([observation(run_id="sample-z")])
    result = module.build_baseline([observation()], history=iter(history))
    assert [r["run_id"] for r in result] == ["sample-z", "sample-a"]


def test_history_rejects_overwrite():
    history = module.build_baseline([observation()])
    original = deepcopy(history)
    with pytest.raises(ValueError, match="already in history"):
        module.build_baseline([observation(4, 1)], history=history)
    assert history == original


def test_duplicate_history_is_rejected():
    history = module.build_baseline([observation()])
    with pytest.raises(ValueError, match="duplicate history"):
        module.build_baseline([], history=history + history)


def test_empty_input_returns_independent_history():
    assert module.build_baseline([]) == []
    history = module.build_baseline([observation()])
    result = module.build_baseline([], history=history)
    assert result == history
    assert result is not history
    assert result[0] is not history[0]


@pytest.mark.parametrize("field", ["raw_unresolved", "canonical_unresolved"])
@pytest.mark.parametrize("value", [-1, True, 1.5, "3", None])
def test_invalid_counts_are_rejected(field, value):
    # Synthetic invalid values must never silently become plausible counts.
    item = {**observation(), field: value}
    with pytest.raises(ValueError, match=field):
        module.build_baseline([item])


@pytest.mark.parametrize("value", [-1, True, 1.5, "3", None])
def test_invalid_supplied_budget_is_rejected_even_when_unused(value):
    with pytest.raises(ValueError, match="budget"):
        module.build_baseline([], budgets={"provider-a": value})


@pytest.mark.parametrize("field", ["run_id", "provider"])
@pytest.mark.parametrize("value", ["", " ", None, 3])
def test_invalid_group_keys_are_rejected(field, value):
    with pytest.raises(ValueError, match=field):
        module.build_baseline([{**observation(), field: value}])


def test_budget_provider_key_is_validated():
    with pytest.raises(ValueError, match="provider"):
        module.build_baseline([], budgets={"": 3})


def test_missing_count_is_not_fabricated():
    item = observation()
    del item["raw_unresolved"]
    with pytest.raises(ValueError, match="raw_unresolved"):
        module.build_baseline([item])


def test_no_file_io_and_caller_file_metadata_preserved(tmp_path, monkeypatch):
    target = tmp_path / "history.json"
    target.write_text("synthetic caller content", encoding="utf-8")
    before_content = target.read_bytes()
    before_metadata = target.stat()

    def forbidden_open(*args, **kwargs):
        pytest.fail("arithmetic must not open files")

    with monkeypatch.context() as patch:
        patch.setattr(builtins, "open", forbidden_open)
        patch.setattr(Path, "open", forbidden_open)
        rows = module.build_baseline([observation()])
    assert rows[0]["delta"] == 9  # 12 - 3, as in the hand-calculated case.
    after_metadata = target.stat()
    assert after_metadata == before_metadata
    assert (after_metadata.st_ino, after_metadata.st_mode, after_metadata.st_size,
            after_metadata.st_atime_ns, after_metadata.st_mtime_ns,
            after_metadata.st_ctime_ns) == (
        before_metadata.st_ino, before_metadata.st_mode, before_metadata.st_size,
        before_metadata.st_atime_ns, before_metadata.st_mtime_ns,
        before_metadata.st_ctime_ns,
    )
    assert target.read_bytes() == before_content
