#!/usr/bin/env python3
# ABOUTME: TDD tests for ASTM deterministic classifier (WRK-1188 Phase 0a)
# ABOUTME: Validates prefix→discipline mapping, title extraction, summary output

"""Tests for phase-b-astm-classifier.py — deterministic ASTM classification."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import sys
sys.path.insert(
    0, str(Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index")
)


# ── Prefix→discipline mapping ────────────────────────────────────────────────


class TestPrefixMapping:
    """ASTM designation prefix → discipline mapping."""

    def test_a_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("A") == "materials"

    def test_b_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("B") == "materials"

    def test_c_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("C") == "materials"

    def test_d_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("D") == "materials"

    def test_e_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("E") == "materials"

    def test_f_prefix_maps_to_materials(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("F") == "materials"

    def test_g_prefix_maps_to_cathodic_protection(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("G") == "cathodic-protection"

    def test_unknown_prefix_returns_other(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("Z") == "other"

    def test_lowercase_prefix_works(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("a") == "materials"

    def test_empty_prefix_returns_other(self):
        from phase_b_astm_classifier import prefix_to_discipline
        assert prefix_to_discipline("") == "other"


# ── Title extraction from text header ────────────────────────────────────────


class TestTitleExtraction:
    """Extract real title from ASTM document text header."""

    def test_standard_specification_title(self):
        from phase_b_astm_classifier import extract_title_from_text
        text = (
            "[Page 1]\nDesignation: A 967 – 01e1\n"
            "An American National Standard\n"
            "Standard Specification for\n"
            "Chemical Passivation Treatments for Stainless Steel Parts1\n"
            "This standard is issued under the fixed designation"
        )
        title = extract_title_from_text(text)
        assert "Chemical Passivation" in title

    def test_standard_test_method_title(self):
        from phase_b_astm_classifier import extract_title_from_text
        text = (
            "[Page 1]\nDesignation: G 42 – 96\n"
            "Standard Test Method for\n"
            "Cathodic Disbonding of Pipeline Coatings Subjected to\n"
            "Elevated Temperatures1\n"
            "This standard is issued"
        )
        title = extract_title_from_text(text)
        assert "Cathodic Disbonding" in title

    def test_standard_practice_title(self):
        from phase_b_astm_classifier import extract_title_from_text
        text = (
            "[Page 1]\nDesignation: G 110 – 92\n"
            "Standard Practice for\n"
            "Evaluating Intergranular Corrosion Resistance\n"
            "This standard is issued"
        )
        title = extract_title_from_text(text)
        assert "Corrosion Resistance" in title

    def test_no_text_returns_none(self):
        from phase_b_astm_classifier import extract_title_from_text
        assert extract_title_from_text(None) is None
        assert extract_title_from_text("") is None

    def test_no_pattern_match_returns_none(self):
        from phase_b_astm_classifier import extract_title_from_text
        assert extract_title_from_text("random text with no standard format") is None


# ── Designation extraction ───────────────────────────────────────────────────


class TestDesignationExtraction:
    """Extract ASTM designation prefix from doc_number or title."""

    def test_extract_from_doc_number_with_astm_prefix(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("A967", "ASTM A967 01") == "A"

    def test_extract_from_doc_number_bare(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("G42", "ASTM G42 96") == "G"

    def test_extract_from_title_when_doc_number_empty(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("", "A703 01") == "A"

    def test_extract_from_title_with_astm_prefix(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("", "ASTM A380") == "A"

    def test_extract_from_title_with_space(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("", "A 275 98") == "A"

    def test_returns_none_for_empty(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("", "") is None

    def test_returns_none_for_numeric_only(self):
        from phase_b_astm_classifier import extract_designation_prefix
        assert extract_designation_prefix("123", "456") is None


# ── Summary output format ────────────────────────────────────────────────────


class TestSummaryOutput:
    """Verify summary JSON format matches existing pipeline conventions."""

    def test_classify_row_produces_valid_summary(self):
        from phase_b_astm_classifier import classify_astm_row
        # Simulate a DB row: (id, org, doc_number, title, target_path,
        #                      content_hash, file_size, full_text, word_count)
        row = (
            288, "ASTM", "A967", "ASTM A967 01",
            "/mnt/ace/O&G-Standards/astm/a967.pdf",
            "abc123hash", 1024,
            "[Page 1]\nDesignation: A 967 – 01e1\n"
            "Standard Specification for\n"
            "Chemical Passivation Treatments for Stainless Steel Parts1\n"
            "This standard is issued",
            500,
        )
        result = classify_astm_row(row)
        assert result is not None
        assert result["sha256"] == "abc123hash"
        assert result["discipline"] == "materials"
        assert result["source"] == "og_standards"
        assert result["org"] == "ASTM"
        assert "extraction_method" in result
        assert result["extraction_method"] == "astm_deterministic"
        assert "summary" in result
        assert "keywords" in result
        assert isinstance(result["keywords"], list)

    def test_classify_row_no_hash_returns_none(self):
        from phase_b_astm_classifier import classify_astm_row
        row = (1, "ASTM", "A100", "ASTM A100", "/path", None, 0, "text", 10)
        assert classify_astm_row(row) is None

    def test_classify_row_g_prefix_cathodic(self):
        from phase_b_astm_classifier import classify_astm_row
        row = (
            291, "ASTM", "G42", "ASTM G42 96",
            "/path/g42.pdf", "hash_g42", 512,
            "[Page 1]\nDesignation: G 42 – 96\n"
            "Standard Test Method for\n"
            "Cathodic Disbonding of Pipeline Coatings\n"
            "This standard",
            200,
        )
        result = classify_astm_row(row)
        assert result["discipline"] == "cathodic-protection"

    def test_classify_row_no_text_uses_title_fallback(self):
        from phase_b_astm_classifier import classify_astm_row
        row = (
            292, "ASTM", "E992", "ASTM E 992",
            "/path/e992.pdf", "hash_e992", 256,
            None, 0,
        )
        result = classify_astm_row(row)
        assert result is not None
        assert result["discipline"] == "materials"
        assert result["summary"] == "ASTM E 992"

    def test_ambiguous_doc_flagged(self):
        """Docs where prefix can't be determined are flagged for LLM."""
        from phase_b_astm_classifier import classify_astm_row
        row = (
            999, "ASTM", "", "",
            "/path/unknown.pdf", "hash_unk", 128,
            "Some random text with no designation", 10,
        )
        result = classify_astm_row(row)
        assert result is not None
        assert result["discipline"] == "other"
        assert result["extraction_method"] == "astm_deterministic_ambiguous"


# ── Write summary integration ────────────────────────────────────────────────


class TestWriteSummary:
    """Test that summaries are written to the correct path."""

    def test_write_creates_json_file(self, tmp_path):
        from phase_b_astm_classifier import write_astm_summary
        result = {
            "sha256": "testhash123",
            "discipline": "materials",
            "summary": "Test doc",
            "keywords": ["steel"],
            "source": "og_standards",
            "org": "ASTM",
            "path": "/some/path",
            "extraction_method": "astm_deterministic",
        }
        write_astm_summary(result, summaries_dir=tmp_path)
        out_file = tmp_path / "testhash123.json"
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert data["discipline"] == "materials"
        assert data["llm_method"] == "astm_deterministic"

    def test_write_merges_with_existing(self, tmp_path):
        """If summary file exists, merge (don't overwrite all fields)."""
        from phase_b_astm_classifier import write_astm_summary
        existing = {"sha256": "merge_test", "page_count": 5, "word_count": 1000}
        out_file = tmp_path / "merge_test.json"
        out_file.write_text(json.dumps(existing))

        result = {
            "sha256": "merge_test",
            "discipline": "materials",
            "summary": "Merged doc",
            "keywords": [],
            "source": "og_standards",
            "org": "ASTM",
            "path": "/path",
            "extraction_method": "astm_deterministic",
        }
        write_astm_summary(result, summaries_dir=tmp_path)
        data = json.loads(out_file.read_text())
        assert data["discipline"] == "materials"
        assert data["page_count"] == 5  # preserved from existing


# ── CLI / main integration ───────────────────────────────────────────────────


class TestCLI:
    """Test CLI arg parsing and dry-run mode."""

    def test_dry_run_does_not_write(self, tmp_path):
        """--dry-run should count but not write summary files."""
        from phase_b_astm_classifier import classify_and_write_batch
        rows = [
            (1, "ASTM", "A100", "ASTM A100", "/p", "hash1", 100, "text", 10),
        ]
        stats = classify_and_write_batch(
            rows, summaries_dir=tmp_path, dry_run=True
        )
        assert stats["done"] >= 0
        assert not list(tmp_path.glob("*.json"))

    def test_skip_already_classified(self, tmp_path):
        """Docs that already have discipline in summary should be skipped."""
        from phase_b_astm_classifier import classify_and_write_batch
        # Pre-create a summary with discipline
        (tmp_path / "hash_exists.json").write_text(
            json.dumps({"discipline": "materials"})
        )
        rows = [
            (1, "ASTM", "A100", "ASTM A100", "/p", "hash_exists", 100, "t", 10),
        ]
        stats = classify_and_write_batch(
            rows, summaries_dir=tmp_path, dry_run=False
        )
        assert stats["skipped"] == 1
