"""Synthetic payload contract for issue #2110; no live operational fixtures.

The full example is hand-counted: three read calls plus two search calls make
five tool calls; two gates passed, one failed and one was skipped. These are
fixture counts, not policy limits. The existing reference renderer declares
optional issue references in scripts/workflow/build_session_review.py::_normalize_refs.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "workflow"
sys.path.insert(0, str(WORKFLOW))

import session_close_report as report  # noqa: E402

UNKNOWN = {"state": "unknown", "reason": "not supplied"}
# Supplied synthetic dates are fixed strings; they are not clock measurements.
FULL = {
    "timestamp": "2026-10-15T12:30:00Z",
    "tool_calls": {"total": 5, "by_tool": {"read": 3, "search": 2}},
    "gates": {"passed": 2, "failed": 1, "skipped": 1},
    "context": {"repository": "sample", "branch": "feature/report", "issue": 2110},
    "completion": "Focused checks completed.",
    "next_steps": ["Review the payload contract.", "Add automatic invocation."],
}


def test_minimal_report_has_unknowns():
    assert report.build_report({}) == {
        "timestamp": UNKNOWN,
        "tool_calls": {"total": UNKNOWN, "by_tool": UNKNOWN},
        "gates": {"passed": UNKNOWN, "failed": UNKNOWN, "skipped": UNKNOWN},
        "context": {"repository": UNKNOWN, "branch": UNKNOWN, "issue": UNKNOWN},
        "completion": UNKNOWN,
        "next_steps": UNKNOWN,
    }


def test_full_report_preserves_supplied_evidence():
    supplied = deepcopy(FULL)
    assert report.build_report(supplied) == FULL
    assert supplied == FULL


def test_missing_counts_are_not_inferred():
    # An empty tool map establishes no per-tool records, not a measured total.
    actual = report.build_report({"tool_calls": {"by_tool": {}}, "gates": {"passed": 0}})
    assert actual["tool_calls"] == {"total": UNKNOWN, "by_tool": {}}
    assert actual["gates"] == {"passed": 0, "failed": UNKNOWN, "skipped": UNKNOWN}


def test_zero_and_empty_notes_remain_known():
    actual = report.build_report({
        "tool_calls": {"total": 0, "by_tool": {"read": 0}},
        "completion": "", "next_steps": [],
    })
    assert actual["tool_calls"] == {"total": 0, "by_tool": {"read": 0}}
    assert actual["completion"] == ""
    assert actual["next_steps"] == []


def test_null_evidence_is_explicitly_unknown():
    assert report.build_report(dict.fromkeys(FULL)) == report.build_report({})
    actual = report.build_report({"tool_calls": {"total": None, "by_tool": {"read": None}}})
    assert actual["tool_calls"] == {"total": UNKNOWN, "by_tool": {"read": UNKNOWN}}


def test_optional_context_is_independent():
    actual = report.build_report({"context": {"branch": "feature/report"}})
    assert actual["context"] == {
        "repository": UNKNOWN, "branch": "feature/report", "issue": UNKNOWN,
    }


def test_builder_returns_independent_snapshots():
    supplied = deepcopy(FULL)
    actual = report.build_report(supplied)
    actual["tool_calls"]["by_tool"]["read"] = 0
    actual["next_steps"].clear()
    assert supplied == FULL
    minimal = report.build_report({})
    minimal["timestamp"]["reason"] = "changed"
    assert minimal["gates"]["passed"] == UNKNOWN
    assert report.build_report({})["timestamp"] == UNKNOWN


# Negative one, fractional one, a digit string, bools, containers and non-finite
# numbers are independently invalid counts; none is coerced into an integer.
@pytest.mark.parametrize("value", [-1, 1.5, "3", True, False, [], {}, float("nan"), float("inf")])
@pytest.mark.parametrize("section,field", [
    ("tool_calls", "total"), ("gates", "passed"),
    ("gates", "failed"), ("gates", "skipped"),
])
def test_invalid_count_has_field_only_error(section, field, value):
    with pytest.raises(ValueError) as error:
        report.build_report({section: {field: value}})
    assert str(error.value) == f"{section}.{field}"


def test_dynamic_tool_names_never_appear_in_errors():
    with pytest.raises(ValueError) as error:
        report.build_report({"tool_calls": {"by_tool": {"untrusted-key": "untrusted-value"}}})
    assert str(error.value) == "tool_calls.by_tool"


@pytest.mark.parametrize("tools", [[], "read", {"": 0}, {False: 0}])
def test_invalid_tool_map_has_field_only_error(tools):
    with pytest.raises(ValueError) as error:
        report.build_report({"tool_calls": {"by_tool": tools}})
    assert str(error.value) == "tool_calls.by_tool"


@pytest.mark.parametrize("supplied,field", [
    ([], "input"),
    ({"tool_calls": []}, "tool_calls"),
    ({"gates": "untrusted-value"}, "gates"),
    ({"context": []}, "context"),
    ({"timestamp": {}}, "timestamp"),
    ({"completion": []}, "completion"),
    ({"next_steps": "untrusted-value"}, "next_steps"),
    ({"next_steps": [None]}, "next_steps"),
    ({"context": {"repository": []}}, "context.repository"),
    ({"context": {"branch": False}}, "context.branch"),
    ({"context": {"issue": True}}, "context.issue"),
])
def test_invalid_structure_has_field_only_error(supplied, field):
    with pytest.raises(ValueError) as error:
        report.build_report(supplied)
    assert str(error.value) == field


def test_unrecognized_fields_are_not_exported():
    actual = report.build_report({
        "extra": "untrusted-value", "context": {"extra": "untrusted-value"},
        "tool_calls": {"extra": "untrusted-value"}, "gates": {"extra": "untrusted-value"},
    })
    assert actual == report.build_report({})


def run_cli(text, tmp_path):
    return subprocess.run(
        [sys.executable, str(WORKFLOW / "session_close_report.py")],
        input=text, text=True, capture_output=True, cwd=tmp_path, check=False,
    )


def test_cli_is_one_deterministic_json_object(tmp_path):
    first = run_cli(json.dumps(FULL), tmp_path)
    second = run_cli(json.dumps(FULL, sort_keys=True), tmp_path)
    assert first.returncode == second.returncode == 0
    assert first.stderr == second.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout.splitlines() == [first.stdout.rstrip("\n")]
    assert json.loads(first.stdout) == FULL
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("text,field", [
    ("", "input"), ("untrusted-value", "input"), ("[]", "input"),
    ('{} {}', "input"), ('{"timestamp": null, "timestamp": "duplicate"}', "input"),
    ('{"tool_calls":{"total":"untrusted-value"}}', "tool_calls.total"),
    ('{"gates":{"failed":true}}', "gates.failed"),
    ('{"tool_calls":{"by_tool":{"untrusted-key":-1}}}', "tool_calls.by_tool"),
    ('{"tool_calls":{"total":NaN}}', "input"),
])
def test_cli_errors_do_not_echo_input(text, field, tmp_path):
    result = run_cli(text, tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == field + "\n"
