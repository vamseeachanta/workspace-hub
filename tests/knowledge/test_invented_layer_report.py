"""Synthetic GUARD-1 examples from pyramid-conformance-checks.md Section 5.6.

All expected lines are counted directly in the literal fixtures (one-based),
not computed by the detector. Layer numerals instantiate the policy regexes.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/knowledge/invented_layer_report.py"
POLICY = "docs/document-intelligence/pyramid-conformance-checks.md"


@pytest.fixture
def detector():
    spec = importlib.util.spec_from_file_location("invented_layer_report", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finding(line, file="notes.md"):
    return {"file": file, "line": line, "rule": "GUARD-1"}


def test_prose_hybrid_layer_is_reported(detector):
    text = "# Classification\nThis artifact occupies a hybrid layer.\n"
    assert detector.scan_text(text, "notes.md") == [finding(2)]


@pytest.mark.parametrize("phrase", ["L3-adjacent", "between L5 and L6", "hybrid layer"])
def test_policy_vocabulary_is_reported(detector, phrase):
    assert detector.scan_text(f"Classification: {phrase}.", "notes.md") == [finding(1)]


def test_only_cited_vocabulary_is_reported(detector):
    text = "L3 is canonical. L3_adjacent is an identifier.\nHybrid layering is different.\n"
    assert detector.scan_text(text, "notes.md") == []


def test_formatted_pattern_examples_are_excluded(detector):
    text = (
        'Policy forbids "hybrid layer" and \'L3-adjacent\' classifications.\n'
        "Policy cites “between L5 and L6” and ‘hybrid layer’ as examples.\n"
        "`hybrid layer` and ``L3-adjacent with ` inside`` are code.\n"
        "> Quoted example: hybrid layer\n"
        "```markdown\n"
        "hybrid layer\n"
        "```\n"
        "[hybrid layer](https://example.invalid/pattern)\n"
        "![L3-adjacent](https://example.invalid/image)\n"
        "<https://example.invalid/hybrid layer>\n"
        "https://example.invalid/L3-adjacent\n"
    )
    assert detector.scan_text(text, "notes.md") == []


def test_closed_fence_and_quotes_do_not_hide_later_prose(detector):
    text = (
        'Example: "hybrid layer"; now L3-adjacent.\n'
        "~~~text\n"
        "between L5 and L6\n"
        "~~~\n"
        "This is a hybrid layer.\n"
        'An unmatched " example marker.\n'
        "This is between L5 and L6.\n"
    )
    assert detector.scan_text(text, "notes.md") == [finding(1), finding(5), finding(7)]


def test_fence_delimiter_and_length_must_match(detector):
    text = "````text\n```\nhybrid layer\n~~~~\n````\nL3-adjacent\n"
    assert detector.scan_text(text, "notes.md") == [finding(6)]


def test_unclosed_fence_remains_code(detector):
    assert detector.scan_text("~~~\nhybrid layer\n", "notes.md") == []


def test_multiline_inline_code_preserves_line_numbers(detector):
    text = "An example `hybrid layer\nL3-adjacent` ends.\nNow between L5 and L6.\n"
    assert detector.scan_text(text, "notes.md") == [finding(3)]


def test_unmatched_backtick_does_not_exclude_prose(detector):
    text = "An unmatched ` delimiter.\nThis is a hybrid layer.\n"
    assert detector.scan_text(text, "notes.md") == [finding(2)]


def test_apostrophes_do_not_quote_prose(detector):
    text = "It's a hybrid layer and isn't canonical.\n"
    assert detector.scan_text(text, "notes.md") == [finding(1)]


def test_links_do_not_hide_following_prose(detector):
    text = (
        "[hybrid layer](guide_(draft).md) then L3-adjacent.\n"
        "[between L5 and L6][pattern] then hybrid layer.\n"
        "[pattern]: guide.md 'hybrid layer'\n"
        "[pattern] then between L5 and L6.\n"
        "An undefined [hybrid layer] remains prose.\n"
    )
    assert detector.scan_text(text, "notes.md") == [
        finding(1), finding(2), finding(4), finding(5)
    ]


def test_ordinary_tables_and_policy_keywords_do_not_exclude_prose(detector):
    text = (
        "| Rule | Classification |\n"
        "| --- | --- |\n"
        "| GUARD-1 | hybrid layer |\n"
        "The policy says hybrid layer.\n"
    )
    assert detector.scan_text(text, "notes.md") == [finding(3), finding(4)]


def test_named_policy_rows_are_excluded_narrowly(detector):
    text = (
        "### 5.6 Child Guardrail Checks\n"
        "| GUARD-1 | hybrid layer |\n"
        "| GUARD-2 | L3-adjacent |\n"
        "## 12. Revision History\n"
        "| 2026-04-19 | Parent amendment | not L3-adjacent |\n"
        "### Amendment-driver detail (2026-04-19)\n"
        "| A — Remove invented classification | Section 2 | L3-adjacent |\n"
        "| B — Strengthen GUARD-1 (forbidden inventions) | Section 2 | hybrid layer |\n"
        "| C — Other change | Section 2 | hybrid layer |\n"
        "## Other section\n"
        "| GUARD-1 | hybrid layer |\n"
        "This is a hybrid layer.\n"
    )
    assert detector.scan_text(text, POLICY) == [
        finding(3, POLICY), finding(9, POLICY), finding(11, POLICY), finding(12, POLICY)
    ]
    # The same heading and row labels grant no exemption in other documents.
    assert detector.scan_text(text, "notes.md") == [
        finding(line) for line in (2, 3, 5, 7, 8, 9, 11, 12)
    ]


def test_row_labels_outside_named_sections_are_scanned(detector):
    text = "## Other section\n| 2026-04-19 | Parent amendment | hybrid layer |\n"
    assert detector.scan_text(text, POLICY) == [finding(2, POLICY)]


def test_same_line_has_one_rule_diagnostic(detector):
    text = "L3-adjacent is a hybrid layer between L5 and L6.\n"
    assert detector.scan_text(text, "notes.md") == [finding(1)]


def test_files_are_explicit_sorted_relative_and_unchanged(detector, tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    first = docs / "a.md"
    last = docs / "z.md"
    ignored = docs / "unsupplied.md"
    first.write_text("hybrid layer\n", encoding="utf-8", newline="\n")
    last.write_text("# Heading\nL3-adjacent\n", encoding="utf-8", newline="\n")
    ignored.write_text("hybrid layer\n", encoding="utf-8", newline="\n")
    before = {path: path.read_bytes() for path in docs.iterdir()}
    assert detector.scan_files([last, first, first], root=tmp_path) == [
        finding(1, "docs/a.md"), finding(2, "docs/z.md")
    ]
    assert before == {path: path.read_bytes() for path in docs.iterdir()}


def test_file_outside_explicit_root_is_rejected(detector, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("hybrid layer", encoding="utf-8", newline="\n")
    with pytest.raises(ValueError, match="root"):
        detector.scan_files([outside], root=root)


@pytest.mark.parametrize("source", ["../outside.md", "/absolute.md", "a/../b.md"])
def test_text_source_must_be_relative(detector, source):
    with pytest.raises(ValueError, match="relative"):
        detector.scan_text("hybrid layer", source)


def test_cli_reports_json_without_modifying_input(tmp_path):
    target = tmp_path / "notes.md"
    target.write_text("hybrid layer\n", encoding="utf-8", newline="\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), str(target)],
        text=True, capture_output=True, check=False,
    )
    # Reporting succeeds even with a finding; this command is not a gate.
    assert result.returncode == 0
    assert json.loads(result.stdout) == [finding(1)]
    assert result.stderr == ""
    assert target.read_text(encoding="utf-8") == "hybrid layer\n"


def test_cli_requires_explicit_input(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        text=True, capture_output=True, check=False,
    )
    # argparse documents usage errors as exit status 2.
    assert result.returncode == 2
    assert result.stdout == ""


def test_escaped_backticks_are_prose(detector):
    text = r"Escaped \`hybrid layer\` delimiters." + "\n"
    assert detector.scan_text(text, "notes.md") == [finding(1)]


def test_code_span_cannot_cross_fenced_block(detector):
    text = (
        "Unmatched ` marker.\n"
        "```text\n"
        "An example\n"
        "```\n"
        "This hybrid layer has a trailing ` marker.\n"
    )
    assert detector.scan_text(text, "notes.md") == [finding(5)]


def test_link_cannot_hide_a_later_paragraph(detector):
    text = "[example](unclosed\n\nThis is a hybrid layer.\n)\n"
    assert detector.scan_text(text, "notes.md") == [finding(3)]


def test_invalid_reference_definition_is_prose(detector):
    text = "[example]: hybrid layer\n"
    assert detector.scan_text(text, "notes.md") == [finding(1)]


def test_incomplete_policy_table_row_does_not_crash(detector):
    text = "## 12. Revision History\n| 2026-04-19\nThis is a hybrid layer.\n"
    assert detector.scan_text(text, POLICY) == [finding(3, POLICY)]


def test_symlink_outside_root_is_rejected(detector, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("hybrid layer", encoding="utf-8", newline="\n")
    alias = root / "alias.md"
    alias.symlink_to(outside)
    with pytest.raises(ValueError, match="root"):
        detector.scan_files([alias], root=root)


def test_cli_input_error_does_not_expose_absolute_paths(tmp_path):
    missing = tmp_path / "missing.md"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), str(missing)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 2  # argparse's documented usage-error status
    assert result.stdout == ""
    assert str(tmp_path) not in result.stderr


@pytest.mark.parametrize("indent", ["    ", "\t"])
def test_indented_paragraph_continuation_is_prose(detector, indent):
    text = f"This artifact is a\n{indent}hybrid layer.\n"
    assert detector.scan_text(text, "notes.md") == [finding(2)]


def test_indented_code_after_blank_line_is_excluded(detector):
    text = "Paragraph.\n\n    hybrid layer\n\nL3-adjacent\n"
    assert detector.scan_text(text, "notes.md") == [finding(5)]


@pytest.mark.parametrize("boundary", ["# A", "## A", "- A", "> A", "---\nA"])
def test_code_span_cannot_cross_block_boundary(detector, boundary):
    text = f"Unmatched ` marker.\n{boundary} hybrid layer ending with `\n"
    line = 3 if "\n" in boundary else 2
    expected = [] if boundary.startswith(">") else [finding(line)]
    assert detector.scan_text(text, "notes.md") == expected


@pytest.mark.parametrize("target", [
    "not a valid destination", "guide.md extra", "<broken destination", r"guide\ name.md",
    'guide.md "title" trailing', "guide<bad>.md",
])
def test_invalid_inline_link_remains_prose(detector, target):
    assert detector.scan_text(f"[hybrid layer]({target})", "notes.md") == [finding(1)]


@pytest.mark.parametrize("target", [
    "guide.md", "guide_(draft).md", "<guide with spaces.md>",
    'guide.md "a title"', "guide.md 'a title'", "guide.md (a title)", "",
])
def test_valid_inline_link_is_excluded(detector, target):
    assert detector.scan_text(f"[hybrid layer]({target})", "notes.md") == []
