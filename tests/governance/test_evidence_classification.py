"""Recorded classes cannot strengthen conclusions (issue 3851, 2026).

Expected outcomes follow the truth table written in each test, independently
of the implementation. All byte strings are synthetic, with no solver input.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/governance/evidence_classification.py"


@pytest.fixture
def api():
    spec = importlib.util.spec_from_file_location("evidence_classification", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_unverified(result):
    assert result["classification_independently_verified"] is False
    assert result["provenance_independently_verified"] is False
    assert result["native_qualification"] is False
    assert result["readiness_status"] == "NOT_EVALUATED"
    assert result["solve_authorized"] is False
    assert result["publication_authorized"] is False


@pytest.mark.parametrize("label", [
    "format_reproduction", "native_capture", "verified", "ready", "approved", "unknown"
])
def test_label_only_mutation_leaves_all_conclusions_identical(api, label):
    """Same bytes + same predicates => same conclusions for every label.

    The synthetic record starts with 'result=' and ends with a newline. Each
    predicate therefore returns True by direct inspection, regardless of label.
    """
    payload = b"result=synthetic\n"
    checks = {"record": lambda data: data.startswith(b"result="),
              "newline": lambda data: data.endswith(b"\n")}
    original = api.assess_content(payload, recorded_class="format_reproduction", checks=checks)
    changed = api.assess_content(payload, recorded_class=label, checks=checks)
    assert changed.pop("recorded_class") == label
    original.pop("recorded_class")
    assert changed == original
    assert changed["status"] == "content_checks_passed"
    assert changed["content_check_results"] == {"newline": "PASS", "record": "PASS"}
    assert_unverified(changed)


@pytest.mark.parametrize("payload,expected", [
    (b"result=synthetic\n", "content_checks_passed"),
    (b"other=synthetic\n", "content_checks_failed"),
])
def test_changed_bytes_are_actually_checked(api, payload, expected):
    """Only the first literal starts with 'result='; the second must fail."""
    seen = []

    def check(data):
        seen.append(data)
        return data.startswith(b"result=")

    result = api.assess_content(payload, recorded_class="native_capture", checks={"record": check})
    assert seen == [payload]
    assert result["status"] == expected
    assert_unverified(result)


@pytest.mark.parametrize("values,expected", [
    ([], "content_checks_not_evaluated"),
    ([None], "content_checks_not_evaluated"),
    ([True, None], "content_checks_not_evaluated"),
    ([False, None], "content_checks_failed"),
    ([True, False], "content_checks_failed"),
    ([True, True], "content_checks_passed"),
])
def test_content_truth_table(api, values, expected):
    """Fail dominates unknown; unknown or no checks prevents a pass.

    Complete nonempty sets of literal True results pass. No numerical
    engineering limit or acceptance constant is used.
    """
    checks = {f"check_{index}": lambda data, value=value: value
              for index, value in enumerate(values)}
    result = api.assess_content(b"synthetic", recorded_class="native_capture", checks=checks)
    assert result["status"] == expected
    assert_unverified(result)


@pytest.mark.parametrize("invalid", ["PASS", "False", 1, 0, [], {}, object()])
def test_truthy_or_falsey_non_boolean_check_results_cannot_pass(api, invalid):
    """Only literal booleans and None are in the observation contract."""
    result = api.assess_content(b"synthetic", recorded_class="verified",
                                checks={"malformed": lambda data: invalid})
    assert result["status"] == "content_checks_failed"
    assert result["content_check_results"] == {"malformed": "ERROR"}
    assert_unverified(result)


def test_check_error_is_sanitized_and_other_checks_still_run(api):
    """An unreadable check cannot authenticate origin or suppress a failure."""
    def broken(data):
        raise ValueError("synthetic private diagnostic")

    result = api.assess_content(b"synthetic", recorded_class="native_capture", checks={
        "broken": broken, "valid": lambda data: True})
    assert result["status"] == "content_checks_failed"
    assert result["content_check_results"] == {"broken": "ERROR", "valid": "PASS"}
    assert "synthetic private diagnostic" not in str(result)
    assert_unverified(result)


@pytest.mark.parametrize("payload", [None, "synthetic", bytearray(b"synthetic"), {}])
def test_only_immutable_bytes_are_accepted(api, payload):
    with pytest.raises(ValueError, match="Immutable bytes required"):
        api.assess_content(payload, recorded_class="native_capture", checks={})


@pytest.mark.parametrize("label", [None, "", "   ", True, {}])
def test_nonempty_recorded_label_required(api, label):
    with pytest.raises(ValueError, match="Recorded class required"):
        api.assess_content(b"synthetic", recorded_class=label, checks={})


@pytest.mark.parametrize("checks", [None, [], {"": lambda data: True},
                                     {"  ": lambda data: True}, {True: lambda data: True},
                                     {"check": True}])
def test_invalid_checks_are_rejected_before_execution(api, checks):
    with pytest.raises((TypeError, ValueError), match="Named callable checks required"):
        api.assess_content(b"synthetic", recorded_class="native_capture", checks=checks)


def test_labels_are_preserved_without_interpretation_and_results_are_deterministic(api):
    """The adapter stores the label verbatim; insertion order has no meaning."""
    checks = {"z": lambda data: True, "a": lambda data: None}
    result = api.assess_content(b"", recorded_class=" native_capture ", checks=checks)
    assert result["recorded_class"] == " native_capture "
    assert list(result["content_check_results"]) == ["a", "z"]
    assert list(checks) == ["z", "a"]
    result["content_check_results"]["z"] = "changed"
    again = api.assess_content(b"", recorded_class=" native_capture ", checks=checks)
    assert again["content_check_results"]["z"] == "PASS"


def test_caller_cannot_supply_a_verification_override(api):
    """No 'verified=True' escape hatch is part of this bounded interface."""
    with pytest.raises(TypeError):
        api.assess_content(b"synthetic", recorded_class="native_capture", checks={},
                           provenance_independently_verified=True)


def test_unexpected_check_exception_aborts_without_a_verdict(api):
    """An unsupported failure must escape; there can be no success result."""
    class CheckAbort(Exception):
        pass

    def abort(data):
        raise CheckAbort

    with pytest.raises(CheckAbort):
        api.assess_content(b"synthetic", recorded_class="native_capture", checks={"abort": abort})


def test_worked_example_answers_follow_literal_byte_predicates():
    """Hand derivation: the fixed input starts with 'result=' and ends in LF.

    Both named checks are True for both labels. Removing LF makes exactly
    the newline check False. Hence pass/pass/fail, with no origin conclusion.
    """
    import runpy

    example = MODULE.parents[2] / "examples/governance/recorded_evidence.py"
    run_example = runpy.run_path(str(example))["run_example"]
    result = run_example()
    assert set(result) == {"reproduction", "relabeled", "changed_content"}
    assert result["reproduction"]["recorded_class"] == "format_reproduction"
    assert result["relabeled"]["recorded_class"] == "native_capture"
    for name, status in [("reproduction", "content_checks_passed"),
                         ("relabeled", "content_checks_passed"),
                         ("changed_content", "content_checks_failed")]:
        assert result[name]["status"] == status
        assert_unverified(result[name])
    assert result["changed_content"]["content_check_results"] == {
        "newline": "FAIL", "record": "PASS"}
