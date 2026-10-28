"""Literal synthetic examples for boundary policy Section 7.4 and issue 2382.

Expected rows are hand classified: matching source sets trace; disagreement or
malformed evidence is ambiguous; absence is missing; only a reason plus locator
declares legacy. Issue numbers are synthetic identifiers, not measurements.
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/knowledge/promotion_trail_report.py"
SPEC = importlib.util.spec_from_file_location("promotion_trail_report", SCRIPT)
REPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORTER)


def report(tmp_path, pages, page_logs=(), registry=()):
    return REPORTER.report(tmp_path, {
        "pages": pages, "page_logs": list(page_logs), "registry": list(registry),
    })


def rows(result):
    return [(row["page"], row["status"], row["sources"]) for row in result]


def test_each_supported_trail_is_visible(tmp_path):
    result = report(tmp_path, [
        {"page": "wiki/front.md", "promoted_from": "sources/run.md#finding"},
        {"page": "wiki/logged.md"},
        {"page": "wiki/registered.md", "doc_key": "summary-key"},
    ], page_logs=[{
        "page": "wiki/logged.md", "locator": "wiki/log.md#entry", "promoted_from": "#17",
    }], registry=[{
        "doc_key": "summary-key", "locator": "registry.jsonl#record", "promoted_from": "doc_key:source-key",
    }])
    assert rows(result) == [
        ("wiki/front.md", "traced", ["sources/run.md#finding"]),
        ("wiki/logged.md", "traced", ["#17"]),
        ("wiki/registered.md", "traced", ["doc_key:source-key"]),
    ]
    assert [row["evidence"] for row in result] == [
        [{"mechanism": "metadata", "locator": "wiki/front.md#promoted_from",
          "sources": ["sources/run.md#finding"], "errors": []}],
        [{"mechanism": "page_log", "locator": "wiki/log.md#entry",
          "sources": ["#17"], "errors": []}],
        [{"mechanism": "registry", "locator": "registry.jsonl#record",
          "sources": ["doc_key:source-key"], "errors": []}],
    ]


def test_mutually_agreeing_trails(tmp_path):
    result = report(tmp_path, [{"page": "wiki/a.md", "doc_key": "a", "promoted_from": ["#17", "sources/run.md"]}],
                    [{"page": "wiki/a.md", "locator": "wiki/log.md#entry", "promoted_from": ["sources/run.md", "#17"]}],
                    [{"doc_key": "a", "locator": "registry.jsonl#record", "promoted_from": ["#17", "sources/run.md"]}])
    assert rows(result) == [("wiki/a.md", "traced", ["#17", "sources/run.md"])]
    assert {item["mechanism"] for item in result[0]["evidence"]} == {"metadata", "page_log", "registry"}


@pytest.mark.parametrize("other", ["#18", ["#17", "#18"]])
@pytest.mark.parametrize("mechanism", ["page_logs", "registry"])
def test_conflicting_trails_are_ambiguous(tmp_path, other, mechanism):
    document = {"pages": [{"page": "wiki/a.md", "doc_key": "a", "promoted_from": "#17"}],
                mechanism: [{"page": "wiki/a.md", "locator": "wiki/log.md#entry", "promoted_from": other}
                            if mechanism == "page_logs" else
                            {"doc_key": "a", "locator": "registry.jsonl#record", "promoted_from": other}]}
    result = REPORTER.report(tmp_path, document)
    assert rows(result) == [("wiki/a.md", "ambiguous", ["#17", "#18"])]
    assert "conflicting source sets" in result[0]["errors"]
    assert [item["locator"] for item in result[0]["evidence"]] == [
        "wiki/a.md#promoted_from",
        "wiki/log.md#entry" if mechanism == "page_logs" else "registry.jsonl#record",
    ]


def test_legacy_requires_explicit_evidence(tmp_path):
    result = report(tmp_path, [
        {"page": "wiki/absent.md"},
        {"page": "wiki/bare.md", "legacy": True},
        {"page": "wiki/declared.md", "legacy": {"reason": "Predates recorded lineage", "locator": "notes/history.md#entry"}},
        {"page": "wiki/incomplete.md", "legacy": {"reason": "Old page"}},
    ])
    assert rows(result) == [
        ("wiki/absent.md", "missing", []),
        ("wiki/bare.md", "ambiguous", []),
        ("wiki/declared.md", "legacy", []),
        ("wiki/incomplete.md", "ambiguous", []),
    ]
    assert result[2]["evidence"] == [{
        "mechanism": "legacy", "locator": "notes/history.md#entry", "sources": [],
        "reason": "Predates recorded lineage", "errors": [],
    }]


def test_legacy_does_not_hide_trails(tmp_path):
    result = report(tmp_path, [{"page": "wiki/a.md", "promoted_from": "#17",
                               "legacy": {"reason": "Old page", "locator": "notes.md#entry"}}])
    assert rows(result) == [("wiki/a.md", "ambiguous", ["#17"])]


@pytest.mark.parametrize("legacy", [None, {}, {"reason": " ", "locator": "notes.md"},
    {"reason": "Old page", "locator": "../notes.md"},
    {"reason": "Old page", "locator": "notes.md", "extra": True}])
def test_malformed_legacy_is_not_grandfathered(tmp_path, legacy):
    result = report(tmp_path, [{"page": "wiki/a.md", "legacy": legacy}])
    assert rows(result) == [("wiki/a.md", "ambiguous", [])]
    assert result[0]["evidence"][0]["errors"]


@pytest.mark.parametrize("source", [None, "", [], False, {}, ["#17", None],
    "#0", "doc_key:", "unqualified-key", "[source](sources/run.md)",
    "https://example.invalid/item", "../outside.md", "sources/../run.md",
    "sources/%2e%2e/run.md", "sources/run.md#", "sources\\run.md"])
def test_malformed_links_are_ambiguous(tmp_path, source):
    result = report(tmp_path, [{"page": "wiki/a.md", "promoted_from": source}])
    assert result[0]["status"] == "ambiguous"
    assert result[0]["evidence"][0]["errors"]


@pytest.mark.parametrize("locator", [None, "", "../log.md", "log.md#", "https://example.invalid/log"])
def test_invalid_backlink_cannot_trace_even_with_valid_metadata(tmp_path, locator):
    result = report(tmp_path, [{"page": "wiki/a.md", "promoted_from": "#17"}],
                    [{"page": "wiki/a.md", "locator": locator, "promoted_from": "#17"}])
    assert result[0]["status"] == "ambiguous"
    assert result[0]["evidence"][1]["locator"] == locator


def test_deterministic_without_mutating_inputs(tmp_path):
    document = {"pages": [{"page": "wiki/z.md"}, {"page": "wiki/a.md", "promoted_from": ["#18", "#17", "#17"]}],
                "page_logs": [{"page": "wiki/a.md", "locator": "log.md#z", "promoted_from": ["#17", "#18"]},
                              {"page": "wiki/a.md", "locator": "log.md#a", "promoted_from": ["#18", "#17"]}]}
    original = json.dumps(document)
    result = REPORTER.report(tmp_path, document)
    assert json.dumps(document) == original
    document["pages"].reverse()
    document["page_logs"].reverse()
    assert REPORTER.report(tmp_path, document) == result
    assert rows(result) == [("wiki/a.md", "traced", ["#17", "#18"]), ("wiki/z.md", "missing", [])]


@pytest.mark.parametrize("document", [
    {}, {"pages": {}}, {"pages": [None]},
    {"pages": [{"page": "../outside.md"}]},
    {"pages": [{"page": "wiki/a.md"}, {"page": "wiki/a.md"}]},
    {"pages": [{"page": "wiki/a.md", "doc_key": "same"}, {"page": "wiki/b.md", "doc_key": "same"}]},
    {"pages": [], "page_logs": [{"page": "wiki/unknown.md"}]},
    {"pages": [], "registry": [{"doc_key": "unknown"}]},
    {"pages": [], "page_logs": {}},
])
def test_invalid_manifest_is_rejected(tmp_path, document):
    with pytest.raises(ValueError):
        REPORTER.report(tmp_path, document)


def test_absolute_and_symlink_escape_are_rejected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "escape").symlink_to(outside, target_is_directory=True)
    for source in (str(outside / "source.md"), "escape/source.md"):
        assert report(root, [{"page": "wiki/a.md", "promoted_from": source}])[0]["status"] == "ambiguous"
    with pytest.raises(ValueError):
        report(root, [{"page": "escape/page.md"}])


def run_cli(tmp_path, manifest):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), manifest],
                          capture_output=True, text=True, env=env, check=False)


def test_cli_is_reporting_only_and_does_not_traverse(tmp_path):
    content = '{"pages": [{"page": "wiki/a.md"}]}'
    (tmp_path / "input.json").write_text(content)
    (tmp_path / "unlisted.md").write_bytes(b"\xff")
    result = run_cli(tmp_path, "input.json")
    assert result.returncode == 0  # Successful reporting, even for a missing trail.
    assert rows(json.loads(result.stdout)) == [("wiki/a.md", "missing", [])]
    assert sorted(path.name for path in tmp_path.iterdir()) == ["input.json", "unlisted.md"]
    assert (tmp_path / "input.json").read_text() == content
    assert (tmp_path / "unlisted.md").read_bytes() == b"\xff"


@pytest.mark.parametrize("content", ['{"pages": [], "pages": []}', '{"pages": NaN}', '{'])
def test_cli_rejects_malformed_json(tmp_path, content):
    (tmp_path / "input.json").write_text(content)
    result = run_cli(tmp_path, "input.json")
    assert result.returncode == 2  # argparse-style invalid input exit code.
    assert not result.stdout
    assert "invalid input" in result.stderr
    assert str(tmp_path) not in result.stderr


def test_cli_rejects_manifest_outside_root(tmp_path):
    result = run_cli(tmp_path, "../input.json")
    assert result.returncode == 2  # argparse-style invalid input exit code.
    assert not result.stdout
    assert str(tmp_path) not in result.stderr
