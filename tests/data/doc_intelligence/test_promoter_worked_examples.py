"""Tests for the worked_examples promoter module."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.text_utils import content_hash

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _make_record(
    text,
    document="test.pdf",
    section="1.0",
    page=1,
    domain="naval-architecture",
    manifest="test.pdf",
):
    """Helper to build a worked-example record."""
    return {
        "text": text,
        "source": {"document": document, "section": section, "page": page},
        "domain": domain,
        "manifest": manifest,
    }


def _read_fixture_records():
    """Load the test fixture JSONL."""
    records = []
    fixture = FIXTURES / "worked_examples.jsonl"
    with open(fixture, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# -- parsing ---------------------------------------------------------------


class TestParseExample:
    """Verify extraction of title and expected value from text."""

    def test_basic_extraction(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record(
            "Example 3.1: Calculate hydrostatic pressure at 100m depth.\n"
            "Given: rho = 1025 kg/m3\n"
            "Solution: P = 1025 * 9.81 * 100 = 1,005,525 Pa"
        )
        result = _parse_example(rec)
        assert result is not None
        assert result["number"] == "3.1"
        assert "hydrostatic pressure" in result["title"].lower()
        assert result["expected_value"] == 1005525.0

    def test_decimal_expected_value(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record(
            "Example 5.2: Determine buoyancy force.\n"
            "Given: rho = 1025, V = 2\n"
            "Solution: F_b = 1025 * 9.81 * 2 = 20,110.5 N"
        )
        result = _parse_example(rec)
        assert result is not None
        assert result["expected_value"] == 20110.5

    def test_no_example_pattern_returns_none(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record("This text has no example definition.")
        result = _parse_example(rec)
        assert result is None

    def test_no_solution_line_returns_none(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record(
            "Example 1.1: Some calculation.\n"
            "Given: x = 10\n"
            "The answer is 42."
        )
        result = _parse_example(rec)
        assert result is None

    def test_source_preserved(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record(
            "Example 2.3: Compute drag.\n"
            "Given: Cd = 0.65\n"
            "Solution: F = 0.5 * 0.65 * 1025 * 4 = 1332.5 N",
            document="DNV-RP-C205.pdf",
            section="2.3",
            page=8,
        )
        result = _parse_example(rec)
        assert result["source"]["document"] == "DNV-RP-C205.pdf"
        assert result["domain"] == "naval-architecture"

    def test_single_digit_example_number(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _parse_example,
        )

        rec = _make_record(
            "Example 7: Simple area calculation.\n"
            "Given: L = 10, W = 5\n"
            "Solution: A = 10 * 5 = 50 m2"
        )
        result = _parse_example(rec)
        assert result is not None
        assert result["number"] == "7"
        assert result["expected_value"] == 50.0


# -- rendering -------------------------------------------------------------


class TestRenderTestFile:
    """Verify rendered pytest test file format."""

    def test_content_hash_present(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "3.1",
                "title": "Calculate pressure",
                "expected_value": 1005525.0,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            }
        ]
        output = _render_test_file("test.pdf", examples)
        assert "# content-hash: " in output
        # Hash is 64 hex chars
        for line in output.split("\n"):
            if "content-hash:" in line:
                hash_val = line.split("# content-hash: ")[1].strip()
                assert len(hash_val) == 64
                break

    def test_parametrize_decorator_present(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "3.1",
                "title": "Calculate pressure",
                "expected_value": 1005525.0,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            }
        ]
        output = _render_test_file("test.pdf", examples)
        assert "@pytest.mark.parametrize" in output
        assert "description,expected_approx" in output

    def test_manifest_in_docstring(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "1.1",
                "title": "Test",
                "expected_value": 42.0,
                "source": {"document": "DNV-RP-C205.pdf"},
                "domain": "naval-architecture",
            }
        ]
        output = _render_test_file("DNV-RP-C205.pdf", examples)
        assert "DNV-RP-C205.pdf" in output

    def test_multiple_examples_rendered(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "3.1",
                "title": "Pressure calc",
                "expected_value": 1005525.0,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            },
            {
                "number": "5.2",
                "title": "Buoyancy force",
                "expected_value": 20110.5,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            },
        ]
        output = _render_test_file("test.pdf", examples)
        assert "Pressure calc" in output
        assert "Buoyancy force" in output
        assert "1005525" in output
        assert "20110.5" in output

    def test_empty_examples_returns_empty(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        output = _render_test_file("test.pdf", [])
        assert output == ""

    def test_integer_values_no_decimal(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "1.1",
                "title": "Area",
                "expected_value": 50.0,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            }
        ]
        output = _render_test_file("test.pdf", examples)
        assert "50)" in output or "50," in output
        assert "50.0" not in output

    def test_output_is_valid_python(self):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            _render_test_file,
        )

        examples = [
            {
                "number": "3.1",
                "title": "Test calc",
                "expected_value": 100.0,
                "source": {"document": "test.pdf"},
                "domain": "naval-architecture",
            }
        ]
        output = _render_test_file("test.pdf", examples)
        compile(output, "<test>", "exec")


# -- promote_worked_examples integration -----------------------------------


class TestPromoteWorkedExamples:
    """Integration tests for the full promote_worked_examples function."""

    def test_writes_output_file(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        result = promote_worked_examples(records, tmp_dir)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        out_path = Path(result.files_written[0])
        assert out_path.exists()
        content = out_path.read_text()
        assert "hydrostatic pressure" in content.lower()
        assert "buoyancy force" in content.lower()

    def test_output_path_structure(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        result = promote_worked_examples(records, tmp_dir)
        out_path = Path(result.files_written[0])
        # Should be under tests/promoted/{domain}/test_{manifest_id}_examples.py
        assert "tests/promoted/naval-architecture" in str(out_path)
        assert out_path.name == "test_dnvrpc205pdf_examples.py"

    def test_idempotency_skips_on_second_call(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        promote_worked_examples(records, tmp_dir)
        result2 = promote_worked_examples(records, tmp_dir)
        assert len(result2.files_skipped) == 1
        assert len(result2.files_written) == 0

    def test_dry_run_writes_nothing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        result = promote_worked_examples(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1
        out_path = Path(result.files_written[0])
        assert not out_path.exists()

    def test_empty_records_no_output(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        result = promote_worked_examples([], tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_unparseable_records_skipped(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = [_make_record("No example pattern in this text at all.")]
        result = promote_worked_examples(records, tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_output_is_valid_python(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        result = promote_worked_examples(records, tmp_dir)
        out_path = Path(result.files_written[0])
        content = out_path.read_text()
        compile(content, out_path, "exec")

    def test_multiple_manifests_produce_separate_files(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = [
            _make_record(
                "Example 1.1: Calc A.\nGiven: x=1\nSolution: y = 42 m",
                manifest="doc-a.pdf",
            ),
            _make_record(
                "Example 2.1: Calc B.\nGiven: x=2\nSolution: y = 84 m",
                manifest="doc-b.pdf",
            ),
        ]
        result = promote_worked_examples(records, tmp_dir)
        assert len(result.files_written) == 2

    def test_content_hash_in_output(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.worked_examples import (
            promote_worked_examples,
        )

        records = _read_fixture_records()
        result = promote_worked_examples(records, tmp_dir)
        out_path = Path(result.files_written[0])
        content = out_path.read_text()
        assert "# content-hash: " in content
