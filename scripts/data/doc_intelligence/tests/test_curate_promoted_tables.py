"""Tests for curate_promoted_tables.py — table quality scoring and promotion."""

import csv
import os
import tempfile

import pytest


def _write_csv(path, rows):
    """Helper to write CSV rows to a file."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


@pytest.fixture
def tables_dir():
    """Create a temp directory with sample CSV tables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, "source")
        dst = os.path.join(tmpdir, "promoted")
        os.makedirs(src)

        # Good table: hydrostatic data with numbers
        _write_csv(os.path.join(src, "good_hydro_001.csv"), [
            ["Draft (ft)", "Displacement (LT)", "TPI", "MT1"],
            ["10.0", "2000", "25.3", "450"],
            ["12.0", "2800", "27.1", "520"],
            ["14.0", "3600", "28.9", "590"],
            ["16.0", "4500", "30.2", "660"],
        ])

        # Bad table: OCR garbage
        _write_csv(os.path.join(src, "garbage_001.csv"), [
            ["", ""],
            ["(cid:10)(cid:5)", ""],
            ["g", ""],
        ])

        # Bad table: too few rows
        _write_csv(os.path.join(src, "tiny_001.csv"), [
            ["x", "y"],
        ])

        # Marginal table: has numbers but messy headers
        _write_csv(os.path.join(src, "marginal_001.csv"), [
            ["", "C", "", ""],
            ["1.0", "2.0", "", ""],
            ["3.0", "4.0", "", ""],
            ["5.0", "6.0", "", ""],
        ])

        yield {"source": src, "promoted": dst}


class TestScoreTable:
    """Tests for the table quality scoring function."""

    def test_good_table_scores_high(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            score_table,
        )

        path = os.path.join(tables_dir["source"], "good_hydro_001.csv")
        score, meta = score_table(path)
        assert score >= 0.7, f"Good table scored {score}, expected ≥0.7"
        assert meta["row_count"] == 5
        assert meta["numeric_ratio"] > 0.5

    def test_garbage_table_scores_low(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            score_table,
        )

        path = os.path.join(tables_dir["source"], "garbage_001.csv")
        score, _ = score_table(path)
        assert score < 0.3, f"Garbage table scored {score}, expected <0.3"

    def test_tiny_table_scores_low(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            score_table,
        )

        path = os.path.join(tables_dir["source"], "tiny_001.csv")
        score, meta = score_table(path)
        assert score < 0.3, f"Tiny table scored {score}, expected <0.3"
        assert meta["row_count"] <= 2


class TestCurateTables:
    """Tests for the main curation pipeline."""

    def test_promotes_good_rejects_bad(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            curate_tables,
        )

        report = curate_tables(
            tables_dir["source"],
            tables_dir["promoted"],
            min_score=0.5,
        )
        promoted_files = os.listdir(tables_dir["promoted"])
        assert "good_hydro_001.csv" in promoted_files
        assert "garbage_001.csv" not in promoted_files
        assert "tiny_001.csv" not in promoted_files
        assert report["promoted_count"] >= 1
        assert report["rejected_count"] >= 2

    def test_report_contains_scores(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            curate_tables,
        )

        report = curate_tables(
            tables_dir["source"],
            tables_dir["promoted"],
            min_score=0.5,
        )
        assert "table_scores" in report
        assert len(report["table_scores"]) == 4  # all 4 tables scored

    def test_empty_source_dir(self):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            curate_tables,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "empty")
            dst = os.path.join(tmpdir, "out")
            os.makedirs(src)
            report = curate_tables(src, dst, min_score=0.5)
            assert report["promoted_count"] == 0
            assert report["rejected_count"] == 0


class TestDetectCidGarbage:
    """Tests for OCR artifact detection."""

    def test_cid_pattern_detected(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            score_table,
        )

        path = os.path.join(tables_dir["source"], "garbage_001.csv")
        _, meta = score_table(path)
        assert meta["has_cid_artifacts"] is True

    def test_clean_table_no_cid(self, tables_dir):
        from scripts.data.doc_intelligence.curate_promoted_tables import (
            score_table,
        )

        path = os.path.join(tables_dir["source"], "good_hydro_001.csv")
        _, meta = score_table(path)
        assert meta["has_cid_artifacts"] is False
