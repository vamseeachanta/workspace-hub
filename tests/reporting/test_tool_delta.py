"""Synthetic contract examples; expected results are independent hand decisions.

No observations are collected. The literal truth table below is the comparison
basis: installation proves presence, usability proves success, failure proves a
failed check, and missing evidence proves neither success nor failure. Returning
evidence alone cannot prove improvement. An absent previous run is distinct from
an observed empty run. All counts and formatting values are hand enumerations of
these examples, rather than measurements or values computed by the implementation.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/reporting/tool_delta.py"
SPEC = importlib.util.spec_from_file_location("tool_delta", MODULE_PATH)
delta = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delta)


def record(state, role="analysis", tool="formatter"):
    return {"role": role, "tool": tool, "state": state}


# Hand-derived table: (before, after, change, reason, severity). There are four
# states in each dimension; every ordered pair is listed explicitly. A failed
# check remains an error even when unchanged. Missing evidence takes precedence
# over equality. Failure -> installation cannot establish recovery.
TRANSITIONS = [
    ("installed", "installed", "unchanged", "STATE_UNCHANGED", "info"),
    ("installed", "usable", "improved", "TOOL_PROMOTED", "info"),
    ("installed", "failed", "regressed", "TOOL_FAILED", "error"),
    ("installed", "missing_evidence", "unknown", "EVIDENCE_MISSING", "warning"),
    ("usable", "installed", "regressed", "USABILITY_LOST", "warning"),
    ("usable", "usable", "unchanged", "STATE_UNCHANGED", "info"),
    ("usable", "failed", "regressed", "TOOL_FAILED", "error"),
    ("usable", "missing_evidence", "unknown", "EVIDENCE_MISSING", "warning"),
    ("failed", "installed", "unknown", "RECOVERY_UNCONFIRMED", "warning"),
    ("failed", "usable", "recovered", "TOOL_RECOVERED", "info"),
    ("failed", "failed", "unchanged", "STATE_UNCHANGED", "error"),
    ("failed", "missing_evidence", "unknown", "EVIDENCE_MISSING", "warning"),
    ("missing_evidence", "installed", "unknown", "EVIDENCE_RESTORED", "info"),
    ("missing_evidence", "usable", "unknown", "EVIDENCE_RESTORED", "info"),
    ("missing_evidence", "failed", "unknown", "EVIDENCE_RESTORED", "error"),
    ("missing_evidence", "missing_evidence", "unknown", "EVIDENCE_MISSING", "warning"),
]


@pytest.mark.parametrize("before,after,change,reason,severity", TRANSITIONS)
def test_transition_truth_table(before, after, change, reason, severity):
    assert delta.compare_tools([record(after)], [record(before)]) == {
        "schema_version": "1.0",
        "baseline": "available",
        "records": [{
            "role": "analysis", "tool": "formatter", "previous": before,
            "current": after, "change": change, "reason_code": reason,
            "severity": severity,
        }],
    }


@pytest.mark.parametrize("state,severity", [
    ("installed", "unknown"), ("usable", "unknown"),
    ("failed", "error"), ("missing_evidence", "unknown"),
])
def test_no_baseline_is_explicit(state, severity):
    expected = {
        "schema_version": "1.0", "baseline": "missing",
        "records": [{
            "role": "analysis", "tool": "formatter", "previous": None,
            "current": state, "change": "no_baseline",
            "reason_code": "NO_BASELINE", "severity": severity,
        }],
    }
    assert delta.compare_tools([record(state)]) == expected
    assert delta.compare_tools([record(state)], None) == expected


@pytest.mark.parametrize("state,severity", [
    ("installed", "info"), ("usable", "info"),
    ("failed", "error"), ("missing_evidence", "warning"),
])
def test_added_is_membership_not_improvement(state, severity):
    # A recorded empty baseline contains no identities: exactly this one is new.
    assert delta.compare_tools([record(state)], []) == {
        "schema_version": "1.0", "baseline": "available",
        "records": [{
            "role": "analysis", "tool": "formatter", "previous": None,
            "current": state, "change": "added", "reason_code": "TOOL_ADDED",
            "severity": severity,
        }],
    }


@pytest.mark.parametrize("state", ["installed", "usable", "failed", "missing_evidence"])
def test_removed_is_membership_not_recovery(state):
    # Disappearance of the sole identity says nothing about successful operation.
    assert delta.compare_tools([], [record(state)]) == {
        "schema_version": "1.0", "baseline": "available",
        "records": [{
            "role": "analysis", "tool": "formatter", "previous": state,
            "current": None, "change": "removed", "reason_code": "TOOL_REMOVED",
            "severity": "warning",
        }],
    }


def test_record_order_does_not_change_delta():
    previous = [record("installed", "review", "lint"), record("usable")]
    current = [record("failed"), record("usable", "review", "lint")]
    expected = {
        "schema_version": "1.0", "baseline": "available",
        "records": [
            {"role": "analysis", "tool": "formatter", "previous": "usable",
             "current": "failed", "change": "regressed",
             "reason_code": "TOOL_FAILED", "severity": "error"},
            {"role": "review", "tool": "lint", "previous": "installed",
             "current": "usable", "change": "improved",
             "reason_code": "TOOL_PROMOTED", "severity": "info"},
        ],
    }
    for before in (previous, list(reversed(previous))):
        for after in (current, list(reversed(current))):
            result = delta.compare_tools(after, before)
            assert result == expected
            assert delta.render_json(result) == delta.render_json(expected)
            assert delta.render_markdown(result) == delta.render_markdown(expected)


def test_identity_is_the_exact_role_and_tool_pair():
    # Same tool in different roles and two tools in one role are distinct.
    records = [record("usable", "review", "lint"), record("usable", "analysis", "lint"),
               record("usable", "analysis", "Lint")]
    result = delta.compare_tools(records, records)
    assert [(row["role"], row["tool"]) for row in result["records"]] == [
        ("analysis", "Lint"), ("analysis", "lint"), ("review", "lint"),
    ]
    assert all(row["change"] == "unchanged" for row in result["records"])


def test_join_includes_removed_and_added_identities_in_sorted_order():
    result = delta.compare_tools(
        [record("usable", tool="new"), record("usable", tool="kept")],
        [record("failed", tool="old"), record("usable", tool="kept")],
    )
    assert [(row["tool"], row["change"]) for row in result["records"]] == [
        ("kept", "unchanged"), ("new", "added"), ("old", "removed"),
    ]


@pytest.mark.parametrize("previous,baseline", [(None, "missing"), ([], "available")])
def test_empty_runs_keep_baseline_status(previous, baseline):
    result = delta.compare_tools([], previous)
    assert result == {"schema_version": "1.0", "baseline": baseline, "records": []}
    text = delta.render_markdown(result)
    assert f"Baseline: {baseline}." in text
    assert "No tool records." in text
    if previous is None:
        assert "No baseline; no improvement can be inferred." in text


def test_literal_json_and_markdown_examples():
    # Hand-written full output for the one unchanged identity, including final LF.
    result = delta.compare_tools([record("usable")], [record("usable")])
    assert delta.render_json(result) == '''{
  "baseline": "available",
  "records": [
    {
      "change": "unchanged",
      "current": "usable",
      "previous": "usable",
      "reason_code": "STATE_UNCHANGED",
      "role": "analysis",
      "severity": "info",
      "tool": "formatter"
    }
  ],
  "schema_version": "1.0"
}
'''
    assert delta.render_markdown(result) == (
        "# Tool delta\n\nBaseline: available.\n\n"
        "| Role | Tool | Previous | Current | Change | Severity | Reason |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| analysis | formatter | usable | usable | unchanged | info | STATE\\_UNCHANGED |\n"
    )


def test_markdown_escapes_html_and_markdown_text():
    # Literal entities and backslash escapes keep caller text inside table cells.
    result = delta.compare_tools([
        record("usable", role="a|b", tool='<tag>&[link](url)!`*_~\\'),
    ])
    assert delta.render_markdown(result) == (
        "# Tool delta\n\nBaseline: missing.\n\n"
        "No baseline; no improvement can be inferred.\n\n"
        "| Role | Tool | Previous | Current | Change | Severity | Reason |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| a\\|b | &lt;tag&gt;&amp;\\[link\\]\\(url\\)\\!\\`\\*\\_\\~\\\\ "
        "| absent | usable | no\\_baseline | unknown | NO\\_BASELINE |\n"
    )


@pytest.mark.parametrize("tool,escaped", [
    ("https://example.invalid", r"https\:\/\/example\.invalid"),
    ('"quoted"', "&quot;quoted&quot;"),
    ("&lt;tag&gt;", r"&amp;lt\;tag&amp;gt\;"),
])
def test_markdown_keeps_links_quotes_and_entities_literal(tool, escaped):
    result = delta.compare_tools([record("usable", tool=tool)])
    assert f"| analysis | {escaped} | absent |" in delta.render_markdown(result)


def test_unicode_identities_round_trip_without_normalization():
    # These visually similar spellings have different Unicode code points.
    current = [record("usable", tool="café"), record("usable", tool="cafe\u0301")]
    result = delta.compare_tools(current, current)
    assert [row["tool"] for row in result["records"]] == ["cafe\u0301", "café"]
    assert json.loads(delta.render_json(result)) == result
    assert "café" in delta.render_json(result)


@pytest.mark.parametrize("separator", ["\n", "\r", "\t", "\x00", "\x1b", "\x7f", "\u2028", "\u2029"])
def test_identity_cannot_break_output_lines(separator):
    with pytest.raises(ValueError, match="current: invalid tool"):
        delta.compare_tools([record("usable", tool=f"a{separator}b")])


@pytest.mark.parametrize("records,message", [
    (None, "expected a list"), ({}, "expected a list"),
    ("usable", "expected a list"), ((record("usable"),), "expected a list"),
    ([None], "expected a record"), ([[]], "expected a record"),
    ([{}], "expected role, tool and state"),
    ([{"role": "analysis", "tool": "formatter"}], "expected role, tool and state"),
    ([dict(record("usable"), extra="value")], "expected role, tool and state"),
    ([record("other")], "invalid state"), ([record(None)], "invalid state"),
    ([record([])], "invalid state"), ([record(True)], "invalid state"),
    ([record("usable", role="")], "invalid role"),
    ([record("usable", role=" ")], "invalid role"),
    ([record("usable", role=" analysis")], "invalid role"),
    ([record("usable", tool="formatter ")], "invalid tool"),
    ([record("usable", tool=None)], "invalid tool"),
    ([record("usable", role=[])], "invalid role"),
])
def test_malformed_records_have_clear_errors(records, message):
    with pytest.raises(ValueError, match=f"current: {message}"):
        delta.compare_tools(records)


def test_previous_records_are_validated_too():
    with pytest.raises(ValueError, match="previous: invalid state"):
        delta.compare_tools([], [record("other")])


@pytest.mark.parametrize("which", ["current", "previous"])
@pytest.mark.parametrize("second_state", ["usable", "failed"])
def test_duplicate_identities_are_rejected_without_echoing_values(which, second_state):
    repeated = [record("usable"), record(second_state)]
    with pytest.raises(ValueError) as error:
        delta.compare_tools(repeated if which == "current" else [],
                            repeated if which == "previous" else [])
    assert str(error.value) == f"{which}: duplicate role/tool identity"


def test_caller_records_files_and_metadata_are_preserved(tmp_path):
    # These are disposable caller-owned fixtures, including metadata-like files.
    current_path = tmp_path / "current.json"
    previous_path = tmp_path / "previous.json"
    metadata = tmp_path / ".git"
    metadata.mkdir()
    paths = [current_path, previous_path, metadata / "HEAD", metadata / "index"]
    current_path.write_text(json.dumps([record("usable")]), encoding="utf-8")
    previous_path.write_text(json.dumps([record("failed")]), encoding="utf-8")
    for path in paths[2:]:
        path.write_text("synthetic metadata\n", encoding="utf-8")
    contents = {path: path.read_bytes() for path in paths}
    current = json.loads(contents[current_path])
    previous = json.loads(contents[previous_path])
    original = copy.deepcopy((current, previous))
    before = {path: path.stat() for path in [tmp_path, metadata, *paths]}
    result = delta.compare_tools(current, previous)
    delta.render_json(result)
    delta.render_markdown(result)
    assert (current, previous) == original
    assert {path: path.stat() for path in before} == before
    assert {path: path.read_bytes() for path in paths} == contents
    assert sorted(tmp_path.iterdir()) == sorted([current_path, previous_path, metadata])
