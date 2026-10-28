"""Synthetic contract examples for the failure-counting slice of issue #1880.

Expected counts are hand calculations, independent of the implementation.
Single-record examples contribute one accepted or rejected record and zero to
the other count. Empty inputs contribute zero. No live corpus is read.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts/analysis/session_corpus_summary.py"
)

# Ten lines: eight accepted, two rejected, four distinct synthetic sessions.
# Only a has tool_error/timeout, only b has git_conflict; c and d lack evidence.
# Stop records and tool_error records are deliberately repeated verbatim.
SYNTHETIC_JSONL = '''\
{"session_id":"a","hook_event_name":"Stop","last_assistant_message":"private text"}
{"session_id":"a","hook_event_name":"Stop","last_assistant_message":"private text"}
{"session_id":"a","failure_category":"tool_error"}
{"session_id":"a","failure_category":"tool_error"}
{"session_id":"a","failure_category":"timeout"}
{"session_id":"b","failure_category":"git_conflict"}
{"session_id":"c","hook_event_name":"Stop"}
{broken
{"failure_category":"timeout"}
{"session_id":"d"}
'''

EXPECTED_SUMMARY = {
    "accepted_records": 8,
    "rejected_records": 2,
    "sessions": 4,
    "failure_sessions_by_category": {
        "tool_error": 1,
        "git_conflict": 1,
        "timeout": 1,
    },
    "sessions_without_failure_evidence": 2,
    "tool_calls": None,
    "tdd_compliance": None,
}


@pytest.fixture
def summary_module():
    spec = importlib.util.spec_from_file_location("session_corpus_summary", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_literal_jsonl_counts(summary_module):
    records = summary_module.parse_jsonl(SYNTHETIC_JSONL.splitlines())
    assert summary_module.summarize(records) == EXPECTED_SUMMARY


def test_empty_input_is_not_evidence_of_tool_or_tdd_totals(summary_module):
    assert summary_module.summarize([]) == {
        "accepted_records": 0,
        "rejected_records": 0,
        "sessions": 0,
        "failure_sessions_by_category": {
            "tool_error": 0, "git_conflict": 0, "timeout": 0,
        },
        "sessions_without_failure_evidence": 0,
        "tool_calls": None,
        "tdd_compliance": None,
    }


@pytest.mark.parametrize("record", [
    None, [], True, 7, "text", {},
    {"session_id": None}, {"session_id": 7}, {"session_id": []},
    {"session_id": ""}, {"session_id": " \t"},
    {"session_id": "a", "failure_category": "unclassified"},
    {"session_id": "a", "failure_category": ""},
    {"session_id": "a", "failure_category": []},
    {"session_id": "a", "failure_category": {}},
    {"session_id": "a", "failure_category": True},
])
def test_invalid_records_are_rejected_without_creating_sessions(summary_module, record):
    result = summary_module.summarize([record])
    assert result["accepted_records"] == 0
    assert result["rejected_records"] == 1
    assert result["sessions"] == 0
    assert result["failure_sessions_by_category"] == {
        "tool_error": 0, "git_conflict": 0, "timeout": 0,
    }


@pytest.mark.parametrize("record", [
    {"session_id": "a"},
    {"session_id": "a", "failure_category": None},
    {"session_id": "a", "hook_event_name": "Stop", "tool_calls": 7,
     "tdd_compliance": True, "last_assistant_message": "git conflict timeout error"},
])
def test_missing_explicit_failure_evidence_stays_unknown(summary_module, record):
    result = summary_module.summarize([record])
    assert result["accepted_records"] == 1
    assert result["sessions"] == 1
    assert result["sessions_without_failure_evidence"] == 1
    assert result["failure_sessions_by_category"] == {
        "tool_error": 0, "git_conflict": 0, "timeout": 0,
    }
    assert result["tool_calls"] is None
    assert result["tdd_compliance"] is None


def test_category_counts_are_distinct_affected_sessions(summary_module):
    # Five records, two sessions; both have tool errors, only a has a timeout.
    records = json.loads('''[
        {"session_id":"a","failure_category":"tool_error"},
        {"session_id":"a","failure_category":"tool_error"},
        {"session_id":"a","failure_category":"timeout"},
        {"session_id":"b","failure_category":"tool_error"},
        {"session_id":"b"}
    ]''')
    result = summary_module.summarize(records)
    assert result["accepted_records"] == 5
    assert result["sessions"] == 2
    assert result["sessions_without_failure_evidence"] == 0
    assert result["failure_sessions_by_category"] == {
        "tool_error": 2, "git_conflict": 0, "timeout": 1,
    }


def test_pure_function_accepts_iterators_without_mutating_input(summary_module):
    records = [json.loads('{"session_id":"a","failure_category":"tool_error"}')]
    original = copy.deepcopy(records)
    result = summary_module.summarize(iter(records))
    assert records == original
    assert result["sessions"] == 1
    assert result["failure_sessions_by_category"]["tool_error"] == 1


@pytest.mark.parametrize("line", [
    "{broken", "", "[]", "null", "true",
    '{"session_id":"a","session_id":"b"}',
    '{"session_id":"a","extra":NaN}',
    '{"session_id":"a","extra":Infinity}',
    b'{"session_id":"\xff"}',
    '{"session_id":"a"}'.encode("utf-16"),
])
def test_bad_jsonl_lines_are_rejected_individually(summary_module, line):
    result = summary_module.summarize(summary_module.parse_jsonl([line]))
    assert result["rejected_records"] == 1
    assert result["sessions"] == 0


def test_cli_matches_hand_count_and_does_not_emit_source_data(tmp_path):
    source = tmp_path / "signals.jsonl"
    source.write_text(SYNTHETIC_JSONL, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(source)],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(completed.stdout) == EXPECTED_SUMMARY
    assert completed.stderr == ""
    assert "private text" not in completed.stdout
    assert "session_id" not in completed.stdout
    assert str(source) not in completed.stdout


def test_cli_rejects_invalid_utf8_and_continues(tmp_path):
    # One invalid line followed by one valid line: one rejection, one session.
    source = tmp_path / "signals.jsonl"
    source.write_bytes(b'\xff\n{"session_id":"a","failure_category":"timeout"}\n')
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(source)],
        capture_output=True, text=True, check=True,
    )
    result = json.loads(completed.stdout)
    assert result["accepted_records"] == 1
    assert result["rejected_records"] == 1
    assert result["sessions"] == 1
    assert result["failure_sessions_by_category"]["timeout"] == 1


def test_cli_unreadable_input_reports_no_path_or_partial_summary(tmp_path):
    source = tmp_path / "absent.jsonl"
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(source)],
        capture_output=True, text=True,
    )
    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "unable to read input" in completed.stderr
    assert str(source) not in completed.stderr
