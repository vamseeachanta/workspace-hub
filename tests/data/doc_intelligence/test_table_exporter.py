"""Tests for table_exporter — converts manifest ExtractedTable to CSV files."""

import csv
import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.table_exporter import (
    export_tables_from_manifest,
    export_tables_to_csv,
    tables_to_jsonl_records,
)


@pytest.fixture
def sample_manifest_dict():
    """A manifest dict with tables, as produced by manifest_to_dict."""
    return {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "naval-architecture",
        "metadata": {
            "filename": "DNV-RP-C205.pdf",
            "format": "pdf",
            "size_bytes": 1024,
        },
        "tables": [
            {
                "title": "Table 3-1 Current density",
                "columns": ["Zone", "Density (mA/m2)", "Temperature"],
                "rows": [
                    ["Tropical", "50", "25"],
                    ["Subtropical", "70", "15"],
                    ["Arctic", "90", "5"],
                ],
                "source": {"document": "DNV-RP-C205.pdf", "page": 15},
            },
            {
                "title": None,
                "columns": ["Parameter", "Value"],
                "rows": [["GM", "1.5"], ["KG", "8.2"]],
                "source": {"document": "DNV-RP-C205.pdf", "page": 22},
            },
        ],
        "sections": [],
        "figure_refs": [],
        "extraction_stats": {"tables": 2},
        "errors": [],
    }


@pytest.fixture
def empty_manifest_dict():
    return {
        "version": "1.0.0",
        "tool": "extract-document/1.0.0",
        "domain": "general",
        "metadata": {"filename": "empty.pdf", "format": "pdf", "size_bytes": 0},
        "tables": [],
        "sections": [],
        "figure_refs": [],
        "extraction_stats": {"tables": 0},
        "errors": [],
    }


class TestExportTablesToCsv:
    """Test CSV file generation from table dicts."""

    def test_writes_csv_with_header_and_rows(self, tmp_path, sample_manifest_dict):
        table = sample_manifest_dict["tables"][0]
        out_dir = tmp_path / "tables"
        paths = export_tables_to_csv(
            [table], out_dir, doc_name="DNV-RP-C205"
        )
        assert len(paths) == 1
        csv_path = paths[0]
        assert csv_path.exists()
        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert rows[0] == ["Zone", "Density (mA/m2)", "Temperature"]
        assert rows[1] == ["Tropical", "50", "25"]
        assert len(rows) == 4  # header + 3 data rows

    def test_creates_output_directory(self, tmp_path, sample_manifest_dict):
        table = sample_manifest_dict["tables"][0]
        out_dir = tmp_path / "deep" / "nested" / "tables"
        paths = export_tables_to_csv([table], out_dir, doc_name="test")
        assert out_dir.exists()
        assert len(paths) == 1

    def test_multiple_tables_get_indexed_names(self, tmp_path, sample_manifest_dict):
        tables = sample_manifest_dict["tables"]
        paths = export_tables_to_csv(tables, tmp_path, doc_name="DNV-RP-C205")
        assert len(paths) == 2
        names = {p.name for p in paths}
        # First table has title → sanitized name; second has no title → indexed
        assert len(names) == 2

    def test_titled_table_uses_sanitized_title(self, tmp_path, sample_manifest_dict):
        table = sample_manifest_dict["tables"][0]
        paths = export_tables_to_csv([table], tmp_path, doc_name="doc")
        # Title "Table 3-1 Current density" -> sanitized filename
        assert "current_density" in paths[0].stem or "table_001" in paths[0].stem

    def test_empty_tables_list_returns_empty(self, tmp_path):
        paths = export_tables_to_csv([], tmp_path, doc_name="empty")
        assert paths == []

    def test_table_with_empty_rows_still_writes_header(self, tmp_path):
        table = {
            "title": "Empty table",
            "columns": ["A", "B"],
            "rows": [],
            "source": {"document": "test.pdf", "page": 1},
        }
        paths = export_tables_to_csv([table], tmp_path, doc_name="test")
        assert len(paths) == 1
        with open(paths[0], newline="") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 1  # header only
        assert rows[0] == ["A", "B"]

    def test_idempotent_skips_unchanged(self, tmp_path, sample_manifest_dict):
        table = sample_manifest_dict["tables"][0]
        paths1 = export_tables_to_csv([table], tmp_path, doc_name="doc")
        content1 = paths1[0].read_text()
        paths2 = export_tables_to_csv([table], tmp_path, doc_name="doc")
        content2 = paths2[0].read_text()
        assert content1 == content2
        assert paths1[0] == paths2[0]


class TestExportTablesFromManifest:
    """Test end-to-end manifest -> CSV export."""

    def test_exports_all_tables_from_manifest(self, tmp_path, sample_manifest_dict):
        result = export_tables_from_manifest(
            sample_manifest_dict, tmp_path
        )
        assert result["tables_exported"] == 2
        assert result["csv_paths"]
        assert len(result["csv_paths"]) == 2
        for p in result["csv_paths"]:
            assert Path(p).exists()

    def test_empty_manifest_returns_zero(self, tmp_path, empty_manifest_dict):
        result = export_tables_from_manifest(empty_manifest_dict, tmp_path)
        assert result["tables_exported"] == 0
        assert result["csv_paths"] == []

    def test_result_includes_domain(self, tmp_path, sample_manifest_dict):
        result = export_tables_from_manifest(sample_manifest_dict, tmp_path)
        assert result["domain"] == "naval-architecture"


class TestTablesToJsonlRecords:
    """Test JSONL record generation for promoter integration."""

    def test_generates_records_with_csv_path(self, tmp_path, sample_manifest_dict):
        csv_paths = export_tables_to_csv(
            sample_manifest_dict["tables"], tmp_path, doc_name="DNV-RP-C205"
        )
        records = tables_to_jsonl_records(
            sample_manifest_dict["tables"],
            csv_paths,
            domain="naval-architecture",
            manifest_id="DNV-RP-C205",
        )
        assert len(records) == 2
        for rec in records:
            assert "csv_path" in rec
            assert "domain" in rec
            assert "manifest" in rec
            assert rec["domain"] == "naval-architecture"

    def test_record_includes_title_and_source(self, tmp_path, sample_manifest_dict):
        csv_paths = export_tables_to_csv(
            sample_manifest_dict["tables"], tmp_path, doc_name="DNV-RP-C205"
        )
        records = tables_to_jsonl_records(
            sample_manifest_dict["tables"],
            csv_paths,
            domain="naval-architecture",
            manifest_id="DNV-RP-C205",
        )
        rec = records[0]
        assert rec["title"] == "Table 3-1 Current density"
        assert rec["columns"] == ["Zone", "Density (mA/m2)", "Temperature"]
        assert rec["row_count"] == 3

    def test_untitled_table_gets_fallback(self, tmp_path, sample_manifest_dict):
        csv_paths = export_tables_to_csv(
            sample_manifest_dict["tables"], tmp_path, doc_name="DNV-RP-C205"
        )
        records = tables_to_jsonl_records(
            sample_manifest_dict["tables"],
            csv_paths,
            domain="naval-architecture",
            manifest_id="DNV-RP-C205",
        )
        # Second table has title=None
        assert records[1]["title"] is not None  # should get fallback
