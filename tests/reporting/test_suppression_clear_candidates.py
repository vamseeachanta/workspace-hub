"""Synthetic, independently enumerated evidence for issue #2198.

Issue #2198 requires configurable windows and excludes manual-only/high-risk
records. Window sizes here are fixture choices, not policy defaults. Each test
lists its qualifying runs explicitly; expected evidence never uses the function
under test. Existing audit declarations load_previous_audit and
build_cleared_followup_issue_drafts supply no multi-run threshold.
"""

from copy import deepcopy

import pytest

from suppression_clear_candidates import recommend_suppression_clears


def suppression(identifier="target", **changes):
    return {
        "suppression_id": identifier,
        "manual_only": False,
        "high_risk": False,
        **changes,
    }


def run(reference, observed=False, **changes):
    return {
        "run_ref": reference,
        "complete": True,
        "observations": {"target": observed},
        **changes,
    }


def recommendation(records, runs, window):
    return recommend_suppression_clears(records, runs, clean_run_window=window)


def test_complete_clean_window_recommends_only():
    # a, b, c are three distinct complete absences. Window three qualifies;
    # window four is one short. These counts are obtained by enumeration.
    records = [suppression()]
    runs = [run("a"), run("b"), run("c")]
    before = deepcopy((records, runs))
    assert recommendation(records, runs, 3) == [{
        "suppression_id": "target",
        "recommend_clear": True,
        "reason_codes": ["clean_window_met"],
        "supporting_run_refs": ["a", "b", "c"],
    }]
    assert recommendation(records, runs, 4) == [{
        "suppression_id": "target",
        "recommend_clear": False,
        "reason_codes": ["insufficient_clean_runs"],
        "supporting_run_refs": ["a", "b", "c"],
    }]
    assert (records, runs) == before
    assert recommendation(records, runs, 1)[0]["supporting_run_refs"] == ["c"]


def test_reappearance_resets_window():
    # a,b absent; c present; d absent: only d counts, so window two fails.
    records = [suppression()]
    runs = [run("a"), run("b"), run("c", True), run("d")]
    result = recommendation(records, runs, 2)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == ["observed", "insufficient_clean_runs"]
    assert result["supporting_run_refs"] == ["d"]
    # Appending e makes d,e the complete clean window; a,b never return.
    assert recommendation(records, [*runs, run("e")], 2)[0] == {
        "suppression_id": "target",
        "recommend_clear": True,
        "reason_codes": ["clean_window_met"],
        "supporting_run_refs": ["d", "e"],
    }


def test_manual_high_risk_and_incomplete_never_clear():
    # Two clean runs meet window two, but neither exclusion can recommend.
    records = [suppression("manual", manual_only=True),
               suppression("risky", high_risk=True),
               suppression("both", manual_only=True, high_risk=True)]
    runs = [run(ref, observations={"manual": False, "risky": False, "both": False})
            for ref in ("a", "b")]
    before = deepcopy((records, runs))
    results = recommendation(records, runs, 2)
    assert [entry["recommend_clear"] for entry in results] == [False, False, False]
    assert [entry["reason_codes"] for entry in results] == [
        ["manual_only"], ["high_risk"], ["manual_only", "high_risk"],
    ]
    assert (records, runs) == before
    # a absent; b incomplete; c absent: only c counts, below window two.
    incomplete = [run("a"), run("b", complete=False), run("c")]
    result = recommendation([suppression()], incomplete, 2)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == ["incomplete_run", "insufficient_clean_runs"]
    assert result["supporting_run_refs"] == ["c"]


@pytest.mark.parametrize("gap,reason", [
    (run("gap", observations={}), "missing_observation"),
    (run("gap", observations=None), "unknown_observation"),
    (run("gap", None), "unknown_observation"),
    (run("gap", "false"), "unknown_observation"),
    (run("gap", 0), "unknown_observation"),
    (run("gap", complete=None), "incomplete_run"),
    (run("gap", complete="true"), "incomplete_run"),
    (run("gap", complete=1), "incomplete_run"),
    ({"run_ref": "gap"}, "incomplete_run"),
    (run(""), "unknown_run"),
    (run(None), "unknown_run"),
    (None, "unknown_run"),
])
def test_unknown_or_missing_evidence_breaks_clean_streak(gap, reason):
    # a absent; gap unknown; b absent: exactly one eligible suffix run, b.
    result = recommendation([suppression()], [run("a"), gap, run("b")], 2)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == [reason, "insufficient_clean_runs"]
    assert result["supporting_run_refs"] == ["b"]
    # A subsequent complete c restores window two with b,c only.
    recovered = recommendation(
        [suppression()], [run("a"), gap, run("b"), run("c")], 2,
    )[0]
    assert recovered["recommend_clear"] is True
    assert recovered["supporting_run_refs"] == ["b", "c"]


def test_duplicate_run_does_not_inflate_window_or_reorder_evidence():
    # a,a,b,a contains only two distinct runs, below window three.
    runs = [run("a"), run("a"), run("b"), run("a")]
    result = recommendation([suppression()], runs, 3)[0]
    assert result["recommend_clear"] is False
    assert result["supporting_run_refs"] == ["a", "b"]
    # Replay of a after b's reappearance cannot become a new clean run.
    replay = recommendation([suppression()], [run("a"), run("b", True), run("a")], 1)[0]
    assert replay["recommend_clear"] is False
    assert replay["supporting_run_refs"] == []


@pytest.mark.parametrize("conflict", [run("a", True), run("a", complete=False)])
def test_conflicting_duplicate_is_unknown_evidence(conflict):
    # Both copies of a are ambiguous. Only b can support window two.
    runs = [run("a"), conflict, run("b")]
    before = deepcopy(runs)
    result = recommendation([suppression()], runs, 2)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == ["conflicting_run", "insufficient_clean_runs"]
    assert result["supporting_run_refs"] == ["b"]
    assert runs == before


def test_observations_are_specific_to_each_suppression():
    # a sees both absent; b covers target only. The other record loses a.
    records = [suppression(), suppression("other")]
    runs = [run("a", observations={"target": False, "other": False}), run("b")]
    results = recommendation(records, runs, 2)
    assert results[0]["recommend_clear"] is True
    assert results[0]["supporting_run_refs"] == ["a", "b"]
    assert results[1]["recommend_clear"] is False
    assert results[1]["reason_codes"] == ["missing_observation", "insufficient_clean_runs"]
    assert results[1]["supporting_run_refs"] == []


@pytest.mark.parametrize("field", ["manual_only", "high_risk"])
@pytest.mark.parametrize("unknown", [None, "false", 0])
def test_unknown_policy_flags_cannot_recommend(field, unknown):
    record = suppression(**{field: unknown})
    result = recommendation([record], [run("a")], 1)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == ["unknown_policy"]
    del record[field]
    assert recommendation([record], [run("a")], 1)[0]["recommend_clear"] is False


@pytest.mark.parametrize("window", [0, -1, True, 1.5, "2", None])
def test_window_must_be_explicit_positive_integer(window):
    with pytest.raises(ValueError, match="positive integer"):
        recommendation([suppression()], [run("a")], window)


def test_no_history_and_empty_suppression_collection():
    assert recommendation([], [], 1) == []
    assert recommendation([suppression()], [], 1) == [{
        "suppression_id": "target",
        "recommend_clear": False,
        "reason_codes": ["insufficient_clean_runs"],
        "supporting_run_refs": [],
    }]


@pytest.mark.parametrize("records", [
    [suppression(), suppression()], [suppression("")], [suppression(None)], [None],
])
def test_ambiguous_suppression_identifiers_rejected(records):
    with pytest.raises(ValueError, match="suppression"):
        recommendation(records, [], 1)


def test_returned_evidence_is_independent_of_inputs_and_other_results():
    records = [suppression(), suppression("other")]
    runs = [run("a", observations={"target": False, "other": False})]
    before = deepcopy((records, runs))
    results = recommendation(records, runs, 1)
    results[0]["supporting_run_refs"].append("edited")
    results[0]["reason_codes"].append("edited")
    assert results[1]["supporting_run_refs"] == ["a"]
    assert results[1]["reason_codes"] == ["clean_window_met"]
    assert (records, runs) == before


@pytest.mark.parametrize("gap", [
    run("gap", complete=False), run("gap", observations={}), run("gap", None),
])
def test_replayed_unknown_evidence_still_breaks_the_streak(gap):
    # gap,a,b,gap ends with unknown evidence, so neither a nor b can support
    # window two. Replaying an unknown result cannot hide an evidence gap.
    result = recommendation([suppression()], [gap, run("a"), run("b"), gap], 2)[0]
    assert result["recommend_clear"] is False
    assert result["supporting_run_refs"] == []


def test_duplicate_conflict_does_not_treat_numeric_zero_as_explicit_absence():
    # False is explicit absence; integer zero is unknown, despite Python's
    # equality rule. Reference a is ambiguous, leaving only b, below two.
    result = recommendation([suppression()], [run("a"), run("a", 0), run("b")], 2)[0]
    assert result["recommend_clear"] is False
    assert result["reason_codes"] == ["conflicting_run", "insufficient_clean_runs"]
    assert result["supporting_run_refs"] == ["b"]
