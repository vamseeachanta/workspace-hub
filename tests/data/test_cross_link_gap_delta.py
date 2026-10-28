"""CLI contract tests for the offline cross-link delta command.

Basis: scripts/knowledge/wiki-cross-links.py::format_cross_links_jsonl defines
identity and producer field names. All records and dates below are synthetic.
Independent hand calculation: prior identities {changed, removed, stable} and
current {added, changed, stable} give added={added}, removed={removed}; literal
field comparison gives changed={changed}. All expected payloads are fixture
literals, never values computed by the command. Numeric scores and extensions
are arbitrary synthetic literals used to exercise comparison, not thresholds.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]  # tests/data is two levels below root.
SCRIPT = ROOT / "scripts/data/cross-links/compute-gap-delta.py"
IDENTITY = ("source_wiki", "source_page", "target_wiki", "target_page")


def edge(page="stable", **updates):
    record = {
        "source_wiki": "alpha",
        "source_page": page,
        "target_wiki": "beta",
        "target_page": "reference",
        "link_types": ["shared-topic"],
        "score": 0.5,
        "evidence": "shared-topic",
        "discovered": "2026-01-01",
    }
    record.update(updates)
    return record


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def invoke(arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, arguments)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,  # Local process watchdog in seconds; no network or ingest.
    )


def run_delta(tmp_path, prior, current):
    old, new = tmp_path / "prior.jsonl", tmp_path / "current.jsonl"
    write_jsonl(old, prior)
    write_jsonl(new, current)
    before = (old.read_bytes(), new.read_bytes())
    result = invoke(["--prior", old, "--current", new])
    assert (old.read_bytes(), new.read_bytes()) == before
    return result


def successful_records(result):
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return [json.loads(line) for line in result.stdout.splitlines()]


def assert_rejected(result):
    assert result.returncode != 0
    assert result.stdout == ""
    # Fixed diagnostics must never reflect a filename, argument, or input record.
    assert result.stderr in {
        "error: invalid arguments; use --help for usage\n",
        "error: cannot read prior input\n",
        "error: cannot read current input\n",
        "error: invalid prior JSONL\n",
        "error: invalid current JSONL\n",
        "error: duplicate identity in prior input\n",
        "error: duplicate identity in current input\n",
    }


def test_added_removed_and_changed_edges(tmp_path):
    added, removed, stable = edge("added"), edge("removed"), edge()
    old = edge("changed")
    new = edge("changed", score=0.75, evidence="expanded")
    result = run_delta(tmp_path, [stable, removed, old], [new, stable, added])
    assert successful_records(result) == [
        {"change": "added", "before": None, "after": added},
        {"change": "changed", "before": old, "after": new},
        {"change": "removed", "before": removed, "after": None},
    ]


def test_discovery_date_only_is_unchanged(tmp_path):
    assert successful_records(run_delta(
        tmp_path, [edge()], [edge(discovered="2026-02-02")]
    )) == []


def test_discovery_field_presence_is_ignored(tmp_path):
    old = edge()
    del old["discovered"]
    assert successful_records(run_delta(tmp_path, [old], [edge()])) == []


def test_empty_prior_input(tmp_path):
    record = edge()
    assert successful_records(run_delta(tmp_path, [], [record])) == [
        {"change": "added", "before": None, "after": record}
    ]


def test_empty_current_input(tmp_path):
    record = edge()
    assert successful_records(run_delta(tmp_path, [record], [])) == [
        {"change": "removed", "before": record, "after": None}
    ]


def test_both_empty(tmp_path):
    assert successful_records(run_delta(tmp_path, [], [])) == []


@pytest.mark.parametrize("side", ["prior", "current"])
@pytest.mark.parametrize("difference", [{}, {"score": 0.75}, {"discovered": "later"}])
def test_duplicate_identity_rejected(tmp_path, side, difference):
    duplicate = [edge(), edge(**difference)]
    result = run_delta(
        tmp_path, duplicate if side == "prior" else [],
        duplicate if side == "current" else [],
    )
    assert_rejected(result)
    assert result.stderr == f"error: duplicate identity in {side} input\n"


def test_reordered_equivalent_inputs_have_identical_output(tmp_path):
    old = [edge("removed"), edge("changed"), edge()]
    new = [edge(), edge("changed", score=0.75), edge("added")]
    first = run_delta(tmp_path, old, new)
    # Reverse records and object keys; array order remains literal.
    reordered = [dict(reversed(list(record.items()))) for record in reversed(new)]
    second = run_delta(tmp_path, list(reversed(old)), reordered)
    successful_records(first)
    successful_records(second)
    assert second.stdout == first.stdout


def test_identity_is_directed_and_uses_every_component(tmp_path):
    forward = edge()
    reverse = edge(
        "reference", source_wiki="beta", target_wiki="alpha", target_page="stable"
    )
    distinct = [forward, reverse]
    for field in IDENTITY:
        variant = edge()
        variant[field] += "-other"
        distinct.append(variant)
    result = successful_records(run_delta(tmp_path, [], list(reversed(distinct))))
    # Hand-derived lexical order of the four-component directed tuple.
    expected = [
        forward, distinct[5], distinct[4], distinct[3], distinct[2], reverse
    ]
    assert result == [
        {"change": "added", "before": None, "after": record}
        for record in expected
    ]


@pytest.mark.parametrize("updates", [
    {"link_types": ["different"]}, {"evidence": "different"}, {"score": 0.75},
    {"extension": {"nested": ["value", True, None]}},
    {"link_types": ["shared-topic", "other"]},
])
def test_non_timestamp_changes_preserve_payload(tmp_path, updates):
    old, new = edge(), edge(**updates, discovered="2026-02-02")
    assert successful_records(run_delta(tmp_path, [old], [new])) == [
        {"change": "changed", "before": old, "after": new}
    ]


def test_nested_order_is_ignored_but_list_order_and_types_are_literal(tmp_path):
    old = edge(extension={"first": 1, "second": [True, 1]})
    equivalent = edge(extension={"second": [True, 1], "first": 1})
    assert successful_records(run_delta(tmp_path, [old], [equivalent])) == []
    changed = edge(extension={"first": 1, "second": [1, True]})
    assert successful_records(run_delta(tmp_path, [old], [changed])) == [
        {"change": "changed", "before": old, "after": changed}
    ]


def test_removed_field_is_a_change(tmp_path):
    old, new = edge(), edge()
    del new["evidence"]
    assert successful_records(run_delta(tmp_path, [old], [new])) == [
        {"change": "changed", "before": old, "after": new}
    ]


def test_unicode_and_nested_discovered_are_preserved(tmp_path):
    old = edge("café", extension={"discovered": "before"})
    new = edge("café", extension={"discovered": "after"})
    original = copy.deepcopy([old, new])
    result = run_delta(tmp_path, [old], [new])
    assert successful_records(result) == [
        {"change": "changed", "before": old, "after": new}
    ]
    assert [old, new] == original


@pytest.mark.parametrize("side", ["prior", "current"])
@pytest.mark.parametrize("bad_line", [
    "{reflection-marker", "[]", "null", "true", "{}", "\n",
    '{"source_wiki":"first","source_wiki":"reflection-marker"}',
    '{"value":NaN}', '{"value":Infinity}', '{"value":-Infinity}',
])
def test_malformed_jsonl_rejected_without_partial_output(tmp_path, side, bad_line):
    paths = {name: tmp_path / (name + "-reflection-marker.jsonl")
             for name in ("prior", "current")}
    write_jsonl(paths["prior"], [])
    write_jsonl(paths["current"], [edge("added")])
    # Valid prefix would produce output if the command streamed before validation.
    paths[side].write_text(json.dumps(edge()) + "\n" + bad_line + "\n",
                           encoding="utf-8")
    result = invoke(["--prior", paths["prior"], "--current", paths["current"]])
    assert_rejected(result)
    assert result.stderr == f"error: invalid {side} JSONL\n"


@pytest.mark.parametrize("field", IDENTITY)
@pytest.mark.parametrize("bad_value", [None, [], {}, True, 1, "", "   "])
def test_identity_components_must_be_nonempty_strings(tmp_path, field, bad_value):
    result = run_delta(tmp_path, [], [edge(**{field: bad_value})])
    assert_rejected(result)


@pytest.mark.parametrize("payload", [
    b"\xff\n", json.dumps(edge(extension="\ud800")).encode("ascii"),
])
def test_invalid_text_is_rejected(tmp_path, payload):
    old, new = tmp_path / "old", tmp_path / "reflection-marker"
    old.write_bytes(b"")
    new.write_bytes(payload)
    assert_rejected(invoke(["--prior", old, "--current", new]))


def test_nonfinite_extension_rejected(tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    old.write_text("", encoding="utf-8")
    text = json.dumps(edge())[:-1] + ',"extension":1e999}\n'
    new.write_text(text, encoding="utf-8")
    assert_rejected(invoke(["--prior", old, "--current", new]))


def test_repeated_json_key_in_valid_record_rejected(tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    old.write_text("", encoding="utf-8")
    text = json.dumps(edge())[:-1] + ',"score":0.75}\n'
    new.write_text(text, encoding="utf-8")
    assert_rejected(invoke(["--prior", old, "--current", new]))


@pytest.mark.parametrize("arguments", [
    [], ["--prior", "reflection-marker"],
    ["--prior", "-", "--current", "-"],
    ["--prior", "reflection-marker", "--current", "other", "--unexpected"],
    ["--prior", "reflection-marker", "--curr", "other"],
])
def test_explicit_arguments_required_without_reflection(arguments):
    assert_rejected(invoke(arguments))


@pytest.mark.parametrize("side", ["prior", "current"])
@pytest.mark.parametrize("kind", ["missing", "directory"])
def test_unreadable_local_input_rejected(tmp_path, side, kind):
    valid, invalid = tmp_path / "valid", tmp_path / "reflection-marker"
    valid.write_text("", encoding="utf-8")
    if kind == "directory":
        invalid.mkdir()
    paths = {"prior": valid, "current": valid, side: invalid}
    result = invoke(["--prior", paths["prior"], "--current", paths["current"]])
    assert_rejected(result)
    assert result.stderr == f"error: cannot read {side} input\n"


def test_same_local_file_is_unchanged(tmp_path):
    path = tmp_path / "same"
    write_jsonl(path, [edge()])
    assert successful_records(invoke(["--prior", path, "--current", path])) == []


def test_help_is_self_contained():
    result = invoke(["--help"])
    assert result.returncode == 0
    assert "--prior" in result.stdout and "--current" in result.stdout
    assert "before" in result.stdout and "after" in result.stdout
    assert result.stderr == ""
