"""Tests for tables promoter — CSV copy to promoted directory."""

import json
import shutil
from pathlib import Path

import pytest

from scripts.data.doc_intelligence.promoters.coordinator import PromoteResult
from scripts.data.doc_intelligence.promoters.tables import promote_tables

FIXTURES = Path(__file__).parent / "fixtures" / "promote"


def _setup_project(tmp_dir: Path) -> Path:
    """Copy fixture CSVs into a fake project_root under data/doc-intelligence/."""
    doc_intel = tmp_dir / "data" / "doc-intelligence"
    doc_intel.mkdir(parents=True)
    # Copy the tables/ directory with CSVs
    shutil.copytree(FIXTURES / "tables", doc_intel / "tables")
    return tmp_dir


def _load_records() -> list[dict]:
    """Load the fixture JSONL records."""
    records = []
    with open(FIXTURES / "tables_index.jsonl", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


class TestPromoteTablesBasic:
    """Core promotion: CSV copied to correct domain directory."""

    def test_copies_csv_to_promoted_dir(self, tmp_dir):
        project_root = _setup_project(tmp_dir)
        records = _load_records()
        result = promote_tables(records, project_root)

        assert isinstance(result, PromoteResult)
        assert len(result.files_written) == 2
        assert len(result.errors) == 0

        # Verify files exist under promoted/{domain}/
        for rec in records:
            domain = rec["domain"]
            filename = Path(rec["csv_path"]).name
            dest = project_root / "data" / "standards" / "promoted" / domain / filename
            assert dest.exists(), f"Expected {dest} to exist"
            assert dest.stat().st_size > 0

    def test_csv_content_matches_source(self, tmp_dir):
        project_root = _setup_project(tmp_dir)
        records = _load_records()
        promote_tables(records, project_root)

        rec = records[0]
        src = project_root / "data" / "doc-intelligence" / rec["csv_path"]
        dest = (
            project_root
            / "data"
            / "standards"
            / "promoted"
            / rec["domain"]
            / Path(rec["csv_path"]).name
        )
        assert src.read_text(encoding="utf-8") == dest.read_text(encoding="utf-8")

    def test_domain_directory_created(self, tmp_dir):
        project_root = _setup_project(tmp_dir)
        records = _load_records()
        promote_tables(records, project_root)

        domain_dir = project_root / "data" / "standards" / "promoted" / "naval-architecture"
        assert domain_dir.is_dir()


class TestPromoteTablesEmpty:
    """Empty records should not crash."""

    def test_empty_records_returns_empty_result(self, tmp_dir):
        result = promote_tables([], tmp_dir)
        assert isinstance(result, PromoteResult)
        assert result.files_written == []
        assert result.files_skipped == []
        assert result.errors == []


class TestPromoteTablesMissing:
    """Missing source CSV produces error, not exception."""

    def test_missing_csv_records_error(self, tmp_dir):
        project_root = tmp_dir
        # Don't set up any CSVs — source files are missing
        records = [
            {
                "title": "Ghost Table",
                "columns": ["A"],
                "row_count": 1,
                "csv_path": "tables/nonexistent.csv",
                "source": {"document": "ghost.pdf", "page": 1},
                "domain": "naval-architecture",
                "manifest": "ghost.pdf",
            }
        ]
        result = promote_tables(records, project_root)
        assert len(result.errors) == 1
        assert "nonexistent.csv" in result.errors[0]
        assert result.files_written == []


class TestPromoteTablesIdempotency:
    """Second call skips unchanged files."""

    def test_second_call_skips_unchanged(self, tmp_dir):
        project_root = _setup_project(tmp_dir)
        records = _load_records()

        result1 = promote_tables(records, project_root)
        assert len(result1.files_written) == 2
        assert len(result1.files_skipped) == 0

        result2 = promote_tables(records, project_root)
        assert len(result2.files_written) == 0
        assert len(result2.files_skipped) == 2


class TestPromoteTablesDryRun:
    """Dry run reports what would happen without writing."""

    def test_dry_run_writes_nothing(self, tmp_dir):
        project_root = _setup_project(tmp_dir)
        records = _load_records()

        result = promote_tables(records, project_root, dry_run=True)
        assert len(result.files_written) == 2
        assert len(result.errors) == 0

        # No promoted directory should exist
        promoted = project_root / "data" / "standards" / "promoted"
        if promoted.exists():
            files = list(promoted.rglob("*.csv"))
            assert len(files) == 0, f"dry_run should not create files: {files}"


class TestPromoteTablesRegistration:
    """Promoter registers itself with the coordinator."""

    def test_registered_as_tables(self):
        from scripts.data.doc_intelligence.promoters.coordinator import (
            _PROMOTER_REGISTRY,
        )

        # Import triggers registration
        import scripts.data.doc_intelligence.promoters.tables  # noqa: F401

        assert "tables" in _PROMOTER_REGISTRY
