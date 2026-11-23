"""Tests for deep-extract CLI — single-pass extraction + post-processing."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.deep_extract import (
    deep_extract_manifest,
    generate_extraction_report,
)


@pytest.fixture
def sample_manifest_dict():
    return {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "naval-architecture",
        "metadata": {
            "filename": "DNV-RP-C205.pdf",
            "format": "pdf",
            "size_bytes": 1024,
        },
        "sections": [
            {
                "heading": None,
                "level": 0,
                "text": (
                    "Example 3.1: Calculate hydrostatic pressure.\n"
                    "Given: rho = 1025 kg/m3, g = 9.81 m/s2, d = 100 m\n"
                    "Solution: P = 1025 * 9.81 * 100 = 1,005,525 Pa"
                ),
                "source": {"document": "DNV-RP-C205.pdf", "page": 15},
            },
        ],
        "tables": [
            {
                "title": "Table 3-1 Current density",
                "columns": ["Zone", "Value"],
                "rows": [["Tropical", "50"], ["Arctic", "90"]],
                "source": {"document": "DNV-RP-C205.pdf", "page": 16},
            },
        ],
        "figure_refs": [
            {
                "caption": "Drag coefficients",
                "figure_id": "Figure 5-1",
                "source": {"document": "DNV-RP-C205.pdf", "page": 28},
            },
        ],
        "extraction_stats": {"sections": 1, "tables": 1, "figure_refs": 1},
        "errors": [],
    }


class TestDeepExtractManifest:
    """Test the post-processing pipeline on manifest data."""

    def test_exports_tables_to_csv(self, tmp_path, sample_manifest_dict):
        result = deep_extract_manifest(sample_manifest_dict, tmp_path)
        assert result["tables"]["count"] == 1
        assert len(result["tables"]["csv_paths"]) == 1
        # CSV file should exist
        assert Path(result["tables"]["csv_paths"][0]).exists()

    def test_parses_worked_examples(self, tmp_path, sample_manifest_dict):
        result = deep_extract_manifest(sample_manifest_dict, tmp_path)
        assert result["worked_examples"]["count"] == 1
        ex = result["worked_examples"]["examples"][0]
        assert ex["number"] == "3.1"
        assert ex["expected_value"] == 1005525.0
        assert len(ex["inputs"]) == 3

    def test_generates_chart_metadata(self, tmp_path, sample_manifest_dict):
        result = deep_extract_manifest(sample_manifest_dict, tmp_path)
        assert result["charts"]["count"] == 1
        assert result["charts"]["metadata"][0]["figure_id"] == "Figure 5-1"

    def test_empty_manifest(self, tmp_path):
        manifest = {
            "version": "1.0.0",
            "tool": "extract-document/1.0.0",
            "domain": "general",
            "metadata": {"filename": "empty.pdf", "format": "pdf", "size_bytes": 0},
            "sections": [],
            "tables": [],
            "figure_refs": [],
            "extraction_stats": {},
            "errors": [],
        }
        result = deep_extract_manifest(manifest, tmp_path)
        assert result["tables"]["count"] == 0
        assert result["worked_examples"]["count"] == 0
        assert result["charts"]["count"] == 0


class TestGenerateExtractionReport:
    """Test YAML report generation."""

    def test_report_has_required_fields(self, tmp_path, sample_manifest_dict):
        result = deep_extract_manifest(sample_manifest_dict, tmp_path)
        report = generate_extraction_report(result, "DNV-RP-C205")
        assert report["document"] == "DNV-RP-C205"
        assert "tables" in report["summary"]
        assert "worked_examples" in report["summary"]
        assert "charts" in report["summary"]

    def test_report_counts_match(self, tmp_path, sample_manifest_dict):
        result = deep_extract_manifest(sample_manifest_dict, tmp_path)
        report = generate_extraction_report(result, "DNV-RP-C205")
        assert report["summary"]["tables"] == 1
        assert report["summary"]["worked_examples"] == 1
        assert report["summary"]["charts"] == 1
