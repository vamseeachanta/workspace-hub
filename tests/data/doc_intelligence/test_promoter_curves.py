"""Tests for curves promoter — scaffold Python modules and placeholder CSVs."""

import json
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.coordinator import PromoteResult
from scripts.data.doc_intelligence.promoters.curves import promote_curves

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _load_records() -> list[dict]:
    """Load the fixture JSONL records."""
    records = []
    with open(FIXTURES / "curves_index.jsonl", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class TestPromoteCurvesScaffold:
    """Core: Python scaffold and CSV placeholders are created."""

    def test_scaffold_python_file_created(self, tmp_dir):
        records = _load_records()
        result = promote_curves(records, tmp_dir)

        assert isinstance(result, PromoteResult)
        assert len(result.errors) == 0

        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        assert py_path.exists(), f"Expected {py_path} to exist"

    def test_scaffold_contains_curve_comments(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        content = py_path.read_text(encoding="utf-8")

        assert "S-N Curve for Tubular Joints in Seawater" in content
        assert "Figure 4.1" in content
        assert "Wave Spectrum" in content
        assert "Figure 2.3" in content

    def test_scaffold_contains_source_citations(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        content = py_path.read_text(encoding="utf-8")

        assert "DNV-RP-C203.pdf p.22" in content
        assert "DNV-RP-C205.pdf p.10" in content

    def test_scaffold_contains_csv_paths(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        content = py_path.read_text(encoding="utf-8")

        assert "sn_curve_for_tubular_joints_in_seawater.csv" in content
        assert "wave_spectrum_jonswap.csv" in content


class TestPromoteCurvesCSV:
    """Placeholder CSVs created with headers only."""

    def test_placeholder_csvs_created(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        csv_dir = (
            tmp_dir
            / "data"
            / "standards"
            / "promoted"
            / "naval-architecture"
            / "curves"
        )
        csvs = sorted(csv_dir.glob("*.csv"))
        assert len(csvs) == 2

    def test_csv_contains_headers_only(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        csv_path = (
            tmp_dir
            / "data"
            / "standards"
            / "promoted"
            / "naval-architecture"
            / "curves"
            / "sn_curve_for_tubular_joints_in_seawater.csv"
        )
        content = csv_path.read_text(encoding="utf-8")
        assert content == "x,y\n"


class TestPromoteCurvesContentHash:
    """Content hash is present in scaffold."""

    def test_content_hash_present(self, tmp_dir):
        records = _load_records()
        promote_curves(records, tmp_dir)

        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        content = py_path.read_text(encoding="utf-8")
        assert content.startswith("# content-hash: ")
        hash_line = content.split("\n")[0]
        hash_val = hash_line.split(": ", 1)[1]
        assert len(hash_val) == 64  # SHA-256 hex digest


class TestPromoteCurvesEmpty:
    """Empty records should produce no output."""

    def test_empty_records_returns_empty_result(self, tmp_dir):
        result = promote_curves([], tmp_dir)
        assert isinstance(result, PromoteResult)
        assert result.files_written == []
        assert result.files_skipped == []
        assert result.errors == []


class TestPromoteCurvesIdempotency:
    """Second call skips unchanged files."""

    def test_second_call_skips_unchanged(self, tmp_dir):
        records = _load_records()

        result1 = promote_curves(records, tmp_dir)
        written_count = len(result1.files_written)
        assert written_count == 3  # 1 Python + 2 CSVs
        assert len(result1.files_skipped) == 0

        result2 = promote_curves(records, tmp_dir)
        assert len(result2.files_written) == 0
        assert len(result2.files_skipped) == 3


class TestPromoteCurvesDryRun:
    """Dry run reports without writing files."""

    def test_dry_run_writes_nothing(self, tmp_dir):
        records = _load_records()
        result = promote_curves(records, tmp_dir, dry_run=True)

        assert len(result.files_written) == 3  # would write
        assert len(result.errors) == 0

        # No files should actually exist
        py_path = (
            tmp_dir
            / "digitalmodel"
            / "src"
            / "digitalmodel"
            / "naval_architecture"
            / "curves.py"
        )
        assert not py_path.exists()

        csv_dir = (
            tmp_dir
            / "data"
            / "standards"
            / "promoted"
            / "naval-architecture"
            / "curves"
        )
        assert not csv_dir.exists()


class TestPromoteCurvesRegistration:
    """Promoter registers itself with the coordinator."""

    def test_registered_as_curves(self):
        from scripts.data.doc_intelligence.promoters.coordinator import (
            _PROMOTER_REGISTRY,
        )

        import scripts.data.doc_intelligence.promoters.curves  # noqa: F401

        assert "curves" in _PROMOTER_REGISTRY


class TestPromoteCurvesFileCount:
    """Verify the correct total number of files_written."""

    def test_files_written_count(self, tmp_dir):
        records = _load_records()
        result = promote_curves(records, tmp_dir)

        # 1 Python scaffold + 2 placeholder CSVs = 3
        assert len(result.files_written) == 3
        assert len(result.errors) == 0
