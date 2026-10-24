"""Qualification oracles use synthetic inputs and independent hand calculations.

PEP 485 (2015), Implementation: |a-b| <= max(r*max(|a|, |b|), t).
All acceptance limits here are synthetic test inputs, not design criteria.
"""

import json
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from src.solvers.base import SolverResult
from src.solvers.qualification import (
    Assumption,
    Criterion,
    Status,
    compare_value,
)


def criterion(**overrides):
    """Synthetic reference: force = stiffness * extension = 8 * 2 = 16 N.

    The test author selects absolute tolerance 1 N, relative tolerance 0.
    These values are fixtures, with no claim of engineering acceptance.
    """
    values = {
        "quantity": "force", "expected": 16.0, "units": "N",
        "relative_tolerance": 0.0, "absolute_tolerance": 1.0,
        "reference": "Synthetic hand calculation: 8 N/m * 2 m = 16 N",
        "tolerance_basis": "Synthetic test inputs selected by the test author; not design criteria",
    }
    values.update(overrides)
    return Criterion(**values)


def result(**overrides):
    values = {"success": True, "solver_name": "synthetic", "execution_time_ms": 0,
              "result_data": {"force": 16.0}}
    values.update(overrides)
    return SolverResult(**values)


@pytest.mark.parametrize("observed,status", [
    (16, Status.PASS), (17, Status.PASS), (18, Status.FAIL),
    (-16, Status.FAIL), (True, Status.FAIL), ("16", Status.FAIL),
    (None, Status.FAIL), (float("nan"), Status.FAIL),
    (float("inf"), Status.FAIL), (-float("inf"), Status.FAIL),
    (10**400, Status.FAIL),
])
def test_absolute_comparison(observed, status):
    """|17-16| = 1 passes the inclusive 1 N bound; |18-16| = 2 fails."""
    assert compare_value(criterion(), observed, "N").status == status


@pytest.mark.parametrize("expected,observed,status", [
    (8, 10, Status.PASS), (8, 11, Status.FAIL),
    (-8, -10, Status.PASS), (-8, -11, Status.FAIL),
])
def test_relative_comparison(expected, observed, status):
    """PEP 485: |10-8|=2 <= 0.2*10=2; |11-8|=3 > 0.2*11=2.2.

    Negative inputs have identical absolute differences and magnitudes.
    The relative limit 0.2 is a synthetic test input.
    """
    rule = criterion(expected=expected, relative_tolerance=0.2,
                     absolute_tolerance=0.0)
    assert compare_value(rule, observed, "N").status == status


def test_zero_reference_requires_explicit_absolute_bound():
    """|0.5-0| = 0.5 <= 1; with both limits zero, only exact equality passes."""
    rule = criterion(expected=0)
    assert compare_value(rule, 0.5, "N").status == Status.PASS
    exact = replace(rule, absolute_tolerance=0)
    assert compare_value(exact, 0.5, "N").status == Status.FAIL
    assert compare_value(exact, 0, "N").status == Status.PASS


def test_integer_precision_is_not_silently_lost():
    """Hand difference: (2**53 + 1) - 2**53 = 1, greater than exact bound 0.

    These synthetic integer inputs expose conversion to equal binary64 values.
    """
    rule = criterion(expected=2**53, absolute_tolerance=0)
    assert compare_value(rule, 2**53 + 1, "N").status == Status.FAIL


def test_extreme_finite_values_do_not_overflow_comparison():
    """Synthetic: |M-(-M)|=2M > 0.5M for M=1e308, without overflow."""
    rule = criterion(expected=-1e308, relative_tolerance=0.5, absolute_tolerance=0)
    assert compare_value(rule, 1e308, "N").status == Status.FAIL


@pytest.mark.parametrize("units,status", [(None, Status.NOT_EVALUATED),
                                          ("kN", Status.FAIL),
                                          ("n", Status.FAIL)])
def test_units_are_required_and_never_converted(units, status):
    assert compare_value(criterion(), 16, units).status == status


@pytest.mark.parametrize("field,value", [
    ("expected", float("nan")), ("expected", True),
    ("expected", 10**400), ("absolute_tolerance", -1),
    ("relative_tolerance", -1), ("absolute_tolerance", float("inf")),
    ("relative_tolerance", "0.1"), ("reference", " "),
    ("tolerance_basis", ""), ("units", ""), ("quantity", ""),
])
def test_invalid_criteria_are_rejected(field, value):
    with pytest.raises(ValueError):
        criterion(**{field: value})


def test_success_and_qualification_are_separate():
    raw = result()
    report = raw.qualify([criterion()], output_units={"force": "N"})
    assert report.status == Status.PASS
    assert report.accepted
    assert raw.success and raw.result_data == {"force": 16.0}
    encoded = json.loads(json.dumps(asdict(report), allow_nan=False))
    assert encoded["checks"][0]["criterion"]["reference"] == criterion().reference


@pytest.mark.parametrize("outputs", [None, {}, {"other": 16}])
def test_missing_outputs_are_not_evaluated(outputs):
    report = result(result_data=outputs).qualify(
        [criterion()], output_units={"force": "N"})
    assert report.status == Status.NOT_EVALUATED
    assert not report.accepted
    assert report.checks[0].status == Status.NOT_EVALUATED


def test_empty_criteria_cannot_qualify():
    assert result().qualify([], output_units={}).status == Status.NOT_EVALUATED


def test_failed_execution_cannot_qualify_matching_outputs():
    report = result(success=False).qualify([criterion()], output_units={"force": "N"})
    assert report.status == Status.FAIL
    assert not report.accepted
    assert all(check.status != Status.PASS for check in report.checks)


def test_unresolved_assumptions_block_acceptance_and_are_retained():
    assumption = Assumption("extension", None, "Measurement unavailable")
    report = result().qualify([criterion()], output_units={"force": "N"},
                             assumptions=[assumption])
    assert report.status == Status.NOT_EVALUATED
    assert report.assumptions == (assumption,)
    assert not report.accepted


def test_resolved_assumptions_are_retained():
    assumption = Assumption("extension", "2 m", "Synthetic worked input")
    report = result().qualify([criterion()], output_units={"force": "N"},
                             assumptions=[assumption])
    assert report.accepted
    assert report.assumptions == (assumption,)


@pytest.mark.parametrize("args", [("", "2 m", "test"), ("x", "", "test"),
                                  ("x", "2 m", " ")])
def test_assumption_requires_identity_value_and_basis(args):
    with pytest.raises(ValueError):
        Assumption(*args)


def test_fail_takes_precedence_over_missing_evidence():
    missing = criterion(quantity="missing")
    report = result(result_data={"force": 18}).qualify(
        [criterion(), missing], output_units={"force": "N"})
    assert report.status == Status.FAIL
    assert [check.status for check in report.checks] == [Status.FAIL, Status.NOT_EVALUATED]


def test_duplicate_criteria_are_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        result().qualify([criterion(), criterion()], output_units={"force": "N"})


@pytest.mark.parametrize("overrides", [
    {"success": 1}, {"success": "true"}, {"result_data": []}, {"solver_name": ""},
])
def test_malformed_execution_evidence_is_rejected(overrides):
    with pytest.raises((TypeError, ValueError)):
        result(**overrides).qualify([criterion()], output_units={"force": "N"})


def test_units_mapping_is_required():
    with pytest.raises(TypeError):
        result().qualify([criterion()], output_units=[])


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/solver/qualify_result.py"
EXAMPLE = ROOT / "examples/solver-qualification/synthetic.json"


def run_cli(path):
    return subprocess.run([sys.executable, str(CLI), str(path)], cwd=ROOT,
                          text=True, capture_output=True, check=False)


def test_worked_example():
    """Published fixture answer is the hand product 8 N/m * 2 m = 16 N."""
    completed = run_cli(EXAMPLE)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "PASS"
    assert report["checks"][0]["observed"] == 16


@pytest.mark.parametrize("mutation,exit_code,status", [
    ("wrong", 1, "FAIL"), ("missing", 2, "NOT_EVALUATED"),
    ("unresolved", 2, "NOT_EVALUATED"), ("execution", 1, "FAIL"),
])
def test_cli_rejects_unqualified_results(tmp_path, mutation, exit_code, status):
    payload = json.loads(EXAMPLE.read_text())
    if mutation == "wrong":
        payload["result"]["result_data"]["force"] = 18
    elif mutation == "missing":
        payload["output_units"] = {}
    elif mutation == "execution":
        payload["result"]["success"] = False
    else:
        payload["assumptions"][0]["value"] = None
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload))
    completed = run_cli(path)
    assert completed.returncode == exit_code
    assert json.loads(completed.stdout)["status"] == status


@pytest.mark.parametrize("text", [
    '{"result": {}, "result": {}}', '{"result": NaN}',
    '[]', '{}', '{"result": {"success": "true"}}',
])
def test_cli_invalid_input_is_rejected_without_echoing_input(tmp_path, text):
    path = tmp_path / "invalid.json"
    path.write_text(text)
    completed = run_cli(path)
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.strip() == "Invalid qualification input"
