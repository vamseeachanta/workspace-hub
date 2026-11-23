"""Tests for the constants promoter module."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.text_utils import content_hash

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _make_record(text, document="test.pdf", section="1.0", page=1,
                 domain="naval-architecture", manifest="test.pdf"):
    """Helper to build a constants record."""
    return {
        "text": text,
        "source": {"document": document, "section": section, "page": page},
        "domain": domain,
        "manifest": manifest,
    }


# ── parsing ────────────────────────────────────────────────────────────


class TestParseConstants:
    """Verify extraction of name, value, and unit from text."""

    def test_basic_extraction(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("Steel yield strength = 355 MPa for Grade S355.")
        result = _parse_constant(rec)
        assert result is not None
        assert result["name"] == "STEEL_YIELD_STRENGTH"
        assert result["value"] == "355"
        assert result["unit"] == "MPa"

    def test_extraction_with_slash_unit(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("Seawater density = 1025 kg/m³ at standard conditions.")
        result = _parse_constant(rec)
        assert result is not None
        assert result["name"] == "SEAWATER_DENSITY"
        assert result["value"] == "1025"
        assert "kg/m" in result["unit"]

    def test_extraction_decimal_value(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("Drag coefficient = 0.65 for cylindrical sections.")
        result = _parse_constant(rec)
        assert result is not None
        assert result["value"] == "0.65"

    def test_no_match_returns_none(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("This text has no constant definition in it.")
        result = _parse_constant(rec)
        assert result is None

    def test_negative_value(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("Minimum temperature = -40 °C for arctic operations.")
        result = _parse_constant(rec)
        assert result is not None
        assert result["value"] == "-40"

    def test_scientific_notation(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record("Young modulus = 2.1e11 Pa for structural steel.")
        result = _parse_constant(rec)
        assert result is not None
        assert result["value"] == "2.1e11"

    def test_source_preserved(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _parse_constant,
        )
        rec = _make_record(
            "Density = 7850 kg/m³ per standard.",
            document="DNV-RP-C205.pdf", section="2.3", page=8,
        )
        result = _parse_constant(rec)
        assert result["source"]["document"] == "DNV-RP-C205.pdf"


# ── rendering ──────────────────────────────────────────────────────────


class TestRenderConstantsModule:
    """Verify rendered Python module format."""

    def test_content_hash_header(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        parsed = [{
            "name": "TEST_CONST",
            "value": "42",
            "unit": "m",
            "text": "Test constant = 42 m.",
            "source": {"document": "test.pdf", "section": "1.0", "page": 1},
            "domain": "naval-architecture",
        }]
        output = _render_module(parsed)
        assert output.startswith("# content-hash: ")
        # Hash is 64 hex chars
        first_line = output.split("\n")[0]
        hash_val = first_line.split("# content-hash: ")[1]
        assert len(hash_val) == 64

    def test_screaming_snake_case_constant(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        parsed = [{
            "name": "SEAWATER_DENSITY",
            "value": "1025",
            "unit": "kg/m³",
            "text": "Seawater density = 1025 kg/m³.",
            "source": {"document": "dnv.pdf", "section": "2.3", "page": 8},
            "domain": "naval-architecture",
        }]
        output = _render_module(parsed)
        assert "SEAWATER_DENSITY = 1025" in output

    def test_source_citation_in_docstring(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        parsed = [{
            "name": "YIELD_STRENGTH",
            "value": "355",
            "unit": "MPa",
            "text": "Steel yield strength = 355 MPa.",
            "source": {"document": "EN-10025.pdf", "section": "3.1", "page": 12},
            "domain": "naval-architecture",
        }]
        output = _render_module(parsed)
        assert "EN-10025.pdf" in output
        assert "§3.1" in output

    def test_unit_in_docstring(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        parsed = [{
            "name": "DEPTH",
            "value": "100",
            "unit": "m",
            "text": "Depth = 100 m for design.",
            "source": {"document": "spec.pdf"},
            "domain": "naval-architecture",
        }]
        output = _render_module(parsed)
        assert "Unit: m" in output

    def test_multiple_constants_rendered(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        parsed = [
            {
                "name": "ALPHA",
                "value": "1",
                "unit": "",
                "text": "Alpha = 1.",
                "source": {"document": "a.pdf"},
                "domain": "naval-architecture",
            },
            {
                "name": "BETA",
                "value": "2",
                "unit": "m",
                "text": "Beta = 2 m.",
                "source": {"document": "b.pdf"},
                "domain": "naval-architecture",
            },
        ]
        output = _render_module(parsed)
        assert "ALPHA = 1" in output
        assert "BETA = 2" in output

    def test_empty_parsed_returns_empty(self):
        from scripts.data.doc_intelligence.promoters.constants import (
            _render_module,
        )
        output = _render_module([])
        assert output == ""


# ── promote_constants integration ──────────────────────────────────────


class TestPromoteConstants:
    """Integration tests for the full promote_constants function."""

    def test_writes_output_file(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        records = _read_fixture_records()
        result = promote_constants(records, tmp_dir)
        assert len(result.files_written) == 1
        assert len(result.errors) == 0
        out_path = Path(result.files_written[0])
        assert out_path.exists()
        content = out_path.read_text()
        assert "STEEL_YIELD_STRENGTH" in content
        assert "SEAWATER_DENSITY" in content

    def test_idempotency_skips_on_second_call(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        records = _read_fixture_records()
        promote_constants(records, tmp_dir)
        result2 = promote_constants(records, tmp_dir)
        assert len(result2.files_skipped) == 1
        assert len(result2.files_written) == 0

    def test_dry_run_writes_nothing(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        records = _read_fixture_records()
        result = promote_constants(records, tmp_dir, dry_run=True)
        assert len(result.files_written) == 1
        # But file should not actually exist
        out_path = Path(result.files_written[0])
        assert not out_path.exists()

    def test_empty_records_no_crash(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        result = promote_constants([], tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_unparseable_records_skipped(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        records = [_make_record("No constant definition here at all.")]
        result = promote_constants(records, tmp_dir)
        assert len(result.files_written) == 0
        assert len(result.errors) == 0

    def test_output_is_valid_python(self, tmp_dir):
        from scripts.data.doc_intelligence.promoters.constants import (
            promote_constants,
        )
        records = _read_fixture_records()
        result = promote_constants(records, tmp_dir)
        out_path = Path(result.files_written[0])
        content = out_path.read_text()
        # Should compile without syntax errors
        compile(content, out_path, "exec")


def _read_fixture_records():
    """Load the test fixture JSONL."""
    records = []
    fixture = FIXTURES / "constants.jsonl"
    with open(fixture, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
