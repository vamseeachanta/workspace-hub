"""Synthetic arithmetic oracles for the bounded delta slice of issue #2122.

The issue requests deltas and new regressions, but supplies no policy numbers.
All numbers below are synthetic, with hand calculations in the relevant test.
No live evidence, report output or implementation result supplies an oracle.
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ecosystem_scorecard_delta import canonical_json, compute_deltas


def observation(value, *, definition="elapsed duration", unit="s"):
    return {"definition": definition, "unit": unit, "value": value}


def policy(*, direction="lower", threshold=10, **metadata):
    # Synthetic acceptance limit: duration <= 10 seconds is acceptable.
    return {
        "definition": "elapsed duration", "unit": "s",
        "direction": direction, "threshold": threshold, **metadata,
    }


def compare(previous, current, **kwargs):
    return compute_deltas(
        {"duration": observation(previous)},
        {"duration": observation(current)},
        {"duration": policy(**kwargs)},
    )


def test_delta_matches_hand_calculation():
    # Lower is better. 8 - 12 = -4; 13 - 9 = 4; 7 - 7 = 0.
    # At the synthetic limit 10: only 9 -> 13 is a new regression.
    previous = {"improving": observation(12), "regressing": observation(9),
                "unchanged": observation(7)}
    current = {"improving": observation(8), "regressing": observation(13),
               "unchanged": observation(7)}
    result = compute_deltas(previous, current, {key: policy() for key in current})
    rows = {row["metric"]: row for row in result["metrics"]}
    assert [(rows[key]["delta"], rows[key]["trend"]) for key in sorted(rows)] == [
        (-4, "improving"), (4, "regressing"), (0, "unchanged"),
    ]
    assert result["new_regressions"] == ["regressing"]
    assert rows["improving"]["previous_regression"] is True
    assert rows["improving"]["current_regression"] is False
    assert rows["regressing"]["new_regression"] is True


@pytest.mark.parametrize("previous", [None, {}])
def test_missing_previous_is_unknown(previous):
    result = compute_deltas(previous, {"duration": observation(13)},
                            {"duration": policy()})
    row = result["metrics"][0]
    assert row["delta"] is None
    assert row["trend"] == "unknown"
    assert row["reason"] == "missing_previous"
    assert row["previous_regression"] is None
    assert row["current_regression"] is True
    assert row["new_regression"] is None
    assert result["new_regressions"] == []


def test_incompatible_units_are_not_compared():
    result = compute_deltas({"duration": observation(9, unit="ms")},
                            {"duration": observation(13)},
                            {"duration": policy()})
    row = result["metrics"][0]
    assert row["delta"] is None
    assert row["trend"] == "unknown"
    assert row["reason"] == "incompatible_units"
    assert row["new_regression"] is None
    assert result["new_regressions"] == []


@pytest.mark.parametrize("side", ["previous", "current", "policy"])
@pytest.mark.parametrize("field,value,reason", [
    ("definition", "different duration basis", "incompatible_definitions"),
    ("unit", "ms", "incompatible_units"),
])
def test_metadata_must_match_on_both_snapshots_and_policy(side, field, value, reason):
    inputs = {"previous": {"duration": observation(9)},
              "current": {"duration": observation(13)},
              "policy": {"duration": policy()}}
    inputs[side]["duration"][field] = value
    row = compute_deltas(inputs["previous"], inputs["current"],
                         inputs["policy"])["metrics"][0]
    assert row["delta"] is None
    assert row["reason"] == reason
    assert row["new_regression"] is None


@pytest.mark.parametrize("previous,current,reason", [
    ({"duration": observation(9)}, {}, "missing_current"),
    ({"duration": observation(None)}, {"duration": observation(13)},
     "missing_previous"),
    ({"duration": observation(9)}, {"duration": observation(None)},
     "missing_current"),
    ({}, {}, "missing_previous_and_current"),
])
def test_missing_values_are_unknown(previous, current, reason):
    result = compute_deltas(previous, current, {"duration": policy()})
    row = result["metrics"][0]
    assert row["delta"] is None
    assert row["trend"] == "unknown"
    assert row["reason"] == reason
    assert row["new_regression"] is None
    assert result["new_regressions"] == []


@pytest.mark.parametrize("direction,previous,current,expected", [
    # Synthetic limit 10 is inclusive, with strictly worse values regressed.
    ("lower", 10, 11, True), ("lower", 9, 10, False),
    ("lower", 12, 13, False), ("lower", 13, 13, False),
    ("higher", 10, 9, True), ("higher", 11, 10, False),
    ("higher", 8, 7, False), ("higher", 9, 11, False),
])
def test_new_regression_is_an_acceptance_boundary_crossing(
    direction, previous, current, expected,
):
    row = compare(previous, current, direction=direction)["metrics"][0]
    assert row["new_regression"] is expected


def test_higher_is_better_and_zero_is_an_observation():
    # 3 - 0 = 3 is improving when higher is better; zero is not missing.
    row = compare(0, 3, direction="higher")["metrics"][0]
    assert row["delta"] == 3
    assert row["trend"] == "improving"
    assert row["reason"] is None


def test_fractional_delta_matches_decimal_hand_calculation():
    # Decimal arithmetic: 0.3 - 0.1 = 0.2, crossing the synthetic limit 0.2.
    row = compare(0.1, 0.3, threshold=0.2)["metrics"][0]
    assert row["delta"] == 0.2
    assert row["new_regression"] is True


def test_reordering_produces_identical_canonical_json_without_mutation():
    # Two synthetic metrics share the same declared definition and threshold.
    previous = {"beta": observation(9), "alpha": observation(12)}
    current = {"alpha": observation(8), "beta": observation(13)}
    policies = {"beta": policy(), "alpha": policy()}
    saved = copy.deepcopy((previous, current, policies))

    def reverse(mapping):
        return {key: dict(reversed(list(value.items())))
                for key, value in reversed(list(mapping.items()))}

    first = canonical_json(compute_deltas(previous, current, policies))
    second = canonical_json(compute_deltas(
        reverse(previous), reverse(current), reverse(policies),
    ))
    assert first.encode("utf-8") == second.encode("utf-8")
    assert (previous, current, policies) == saved
    assert [row["metric"] for row in json.loads(first)["metrics"]] == ["alpha", "beta"]


def test_canonical_json_has_literal_expected_bytes():
    # The empty result has no metric observations or regression events.
    assert canonical_json(compute_deltas(None, {}, {})) == (
        '{"metrics":[],"new_regressions":[]}'
    )


def test_full_row_has_literal_canonical_json():
    # 9 - 9 = 0; both values meet the synthetic inclusive limit 10.
    assert canonical_json(compare(9, 9)) == (
        '{"metrics":[{"current_regression":false,"definition":"elapsed duration",'
        '"delta":0,"direction":"lower","metric":"duration","new_regression":false,'
        '"previous_regression":false,"reason":null,"threshold":10,'
        '"trend":"unchanged","unit":"s"}],"new_regressions":[]}'
    )


def test_multiple_new_regressions_are_sorted():
    # Each 9 -> 13 crossing is independently 9 <= 10 < 13.
    previous = {key: observation(9) for key in ("beta", "alpha")}
    current = {key: observation(13) for key in ("beta", "alpha")}
    result = compute_deltas(previous, current, {key: policy() for key in current})
    assert result["new_regressions"] == ["alpha", "beta"]


@pytest.mark.parametrize("field", ["direction", "threshold", "definition", "unit"])
def test_policy_metadata_is_required(field):
    supplied = policy()
    del supplied[field]
    with pytest.raises(ValueError, match=field):
        compute_deltas({}, {"duration": observation(13)}, {"duration": supplied})


def test_observed_metric_requires_explicit_policy():
    with pytest.raises(ValueError, match="policy"):
        compute_deltas({}, {"duration": observation(13)}, {})


@pytest.mark.parametrize("value", [True, "13", float("nan"), float("inf")])
@pytest.mark.parametrize("target", ["previous", "current", "threshold"])
def test_invalid_numbers_are_rejected(value, target):
    previous, current, supplied = observation(9), observation(13), policy()
    if target == "threshold":
        supplied["threshold"] = value
    else:
        {"previous": previous, "current": current}[target]["value"] = value
    with pytest.raises(ValueError, match="finite number"):
        compute_deltas({"duration": previous}, {"duration": current},
                       {"duration": supplied})


def test_invalid_direction_is_rejected():
    with pytest.raises(ValueError, match="direction"):
        compare(9, 13, direction="automatic")


@pytest.mark.parametrize("previous,current,policies", [
    ([], {}, {}), ({}, None, {}), ({}, {}, []),
    ({"duration": None}, {}, {"duration": policy()}),
    ({}, {"duration": observation(13)}, {"duration": None}),
])
def test_invalid_container_shapes_are_rejected(previous, current, policies):
    with pytest.raises(ValueError, match="object"):
        compute_deltas(previous, current, policies)


def test_absent_value_field_requires_explicit_null():
    current = observation(None)
    del current["value"]
    with pytest.raises(ValueError, match="value"):
        compute_deltas({}, {"duration": current}, {"duration": policy()})


@pytest.mark.parametrize("value", ["", " ", None])
@pytest.mark.parametrize("field", ["definition", "unit"])
def test_observation_metadata_requires_nonempty_strings(value, field):
    current = observation(13)
    current[field] = value
    with pytest.raises(ValueError, match=field):
        compute_deltas({}, {"duration": current}, {"duration": policy()})


def test_cli_uses_only_supplied_files(tmp_path):
    paths = [tmp_path / name for name in ("previous.json", "current.json", "policy.json")]
    for path, data in zip(paths, [
        {"duration": observation(9)}, {"duration": observation(13)},
        {"duration": policy()},
    ]):
        path.write_text(json.dumps(data), encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "scripts/reporting/ecosystem_scorecard_delta.py"
    completed = subprocess.run([sys.executable, str(script), *map(str, paths)],
                               cwd=tmp_path, capture_output=True, check=True)
    result = json.loads(completed.stdout)
    # Independently: 13 - 9 = 4, with 9 <= 10 < 13.
    assert result["metrics"][0]["delta"] == 4
    assert result["new_regressions"] == ["duration"]
    assert completed.stdout == (canonical_json(result) + "\n").encode("utf-8")
    assert set(tmp_path.iterdir()) == set(paths)


@pytest.mark.parametrize("invalid", ['{"duration":null,"duration":null}', 'NaN'])
def test_cli_rejects_ambiguous_or_nonfinite_json(tmp_path, invalid):
    paths = [tmp_path / name for name in ("previous.json", "current.json", "policy.json")]
    for path in paths:
        path.write_text(invalid, encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "scripts/reporting/ecosystem_scorecard_delta.py"
    completed = subprocess.run([sys.executable, str(script), *map(str, paths)],
                               cwd=tmp_path, capture_output=True)
    assert completed.returncode != 0
    assert completed.stdout == b""
