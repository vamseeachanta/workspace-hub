"""Tests for marine standards batch processor.

Tests the batch processing pipeline that reads the standards-transfer-ledger,
processes marine domain standards, and updates their status.

Issue: #1621
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers – we import the module under test *after* writing it; for now the
# tests define the expected interface and will be runnable once the script
# is written.  We use importlib so the test file is self-contained.
# ---------------------------------------------------------------------------

def _import_batch_processor():
    """Import the batch processor module."""
    import importlib.util
    script_path = Path(__file__).resolve().parents[2] / (
        "scripts/document-intelligence/batch-process-standards.py"
    )
    spec = importlib.util.spec_from_file_location("batch_process_standards", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_LEDGER = {
    "generated": "2026-03-12",
    "total": 10,
    "summary": {"reference": 5, "wrk_captured": 1, "gap": 2, "done": 2},
    "standards": [
        {
            "id": "DNV-OS-E301",
            "title": "Position Mooring",
            "org": "DNV",
            "domain": "marine",
            "doc_path": "/mnt/ace/standards/DNV-OS-E301.pdf",
            "doc_paths": ["/mnt/ace/standards/DNV-OS-E301.pdf"],
            "status": "reference",
            "wrk_id": None,
            "repo": "digitalmodel",
            "modules": [],
            "implemented_at": None,
            "notes": "Mooring standard",
            "exhausted": False,
            "exhausted_at": None,
            "absorbed_into": [],
        },
        {
            "id": "DNV-RP-C205",
            "title": "Environmental Conditions and Environmental Loads",
            "org": "DNV",
            "domain": "marine",
            "doc_path": "/mnt/ace/standards/DNV-RP-C205.pdf",
            "doc_paths": ["/mnt/ace/standards/DNV-RP-C205.pdf"],
            "status": "reference",
            "wrk_id": None,
            "repo": "digitalmodel",
            "modules": [],
            "implemented_at": None,
            "notes": "Env loads",
            "exhausted": False,
            "exhausted_at": None,
            "absorbed_into": [],
        },
        {
            "id": "API-RP-2SK",
            "title": "Design and Analysis of Stationkeeping Systems",
            "org": "API",
            "domain": "marine",
            "doc_path": "",
            "doc_paths": [],
            "status": "done",
            "wrk_id": "WRK-100",
            "repo": "digitalmodel",
            "modules": [],
            "implemented_at": "2026-01-15",
            "notes": "Already processed",
            "exhausted": False,
            "exhausted_at": None,
            "absorbed_into": [],
        },
        {
            "id": "API-5L",
            "title": "API Specification 5L for Line Pipe",
            "org": "API",
            "domain": "pipeline",
            "doc_path": "/mnt/ace/standards/API-5L.pdf",
            "doc_paths": ["/mnt/ace/standards/API-5L.pdf"],
            "status": "reference",
            "wrk_id": None,
            "repo": "digitalmodel",
            "modules": [],
            "implemented_at": None,
            "notes": "Pipeline standard - not marine",
            "exhausted": False,
            "exhausted_at": None,
            "absorbed_into": [],
        },
        {
            "id": "DNV-OS-F101",
            "title": "Submarine Pipeline Systems",
            "org": "DNV",
            "domain": "marine",
            "doc_path": "/mnt/ace/standards/DNV-OS-F101.pdf",
            "doc_paths": ["/mnt/ace/standards/DNV-OS-F101.pdf"],
            "status": "gap",
            "wrk_id": None,
            "repo": "digitalmodel",
            "modules": [],
            "implemented_at": None,
            "notes": "Subsea pipeline",
            "exhausted": False,
            "exhausted_at": None,
            "absorbed_into": [],
        },
    ],
}


@pytest.fixture
def sample_ledger():
    """Return a deep copy of the sample ledger data."""
    import copy
    return copy.deepcopy(SAMPLE_LEDGER)


@pytest.fixture
def ledger_file(sample_ledger, tmp_path):
    """Write sample ledger to a temp YAML file and return path."""
    ledger_path = tmp_path / "standards-transfer-ledger.yaml"
    with open(ledger_path, "w") as f:
        yaml.dump(sample_ledger, f, default_flow_style=False, allow_unicode=True)
    return ledger_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLedgerReading:
    """Test YAML ledger reading and validation."""

    def test_load_ledger_returns_dict_with_standards(self, ledger_file):
        mod = _import_batch_processor()
        data = mod.load_ledger(str(ledger_file))
        assert isinstance(data, dict)
        assert "standards" in data
        assert len(data["standards"]) == 5

    def test_load_ledger_preserves_all_fields(self, ledger_file):
        mod = _import_batch_processor()
        data = mod.load_ledger(str(ledger_file))
        first = data["standards"][0]
        assert first["id"] == "DNV-OS-E301"
        assert first["domain"] == "marine"
        assert first["status"] == "reference"

    def test_load_ledger_nonexistent_raises(self, tmp_path):
        mod = _import_batch_processor()
        with pytest.raises(FileNotFoundError):
            mod.load_ledger(str(tmp_path / "nope.yaml"))


class TestStatusTransition:
    """Test status transition logic."""

    def test_transition_reference_to_done(self):
        mod = _import_batch_processor()
        entry = {"status": "reference", "implemented_at": None}
        mod.apply_status_transition(entry)
        assert entry["status"] == "done"
        assert entry["implemented_at"] is not None

    def test_transition_gap_to_done(self):
        mod = _import_batch_processor()
        entry = {"status": "gap", "implemented_at": None}
        mod.apply_status_transition(entry)
        assert entry["status"] == "done"

    def test_already_done_is_noop(self):
        mod = _import_batch_processor()
        entry = {"status": "done", "implemented_at": "2026-01-01"}
        mod.apply_status_transition(entry)
        assert entry["status"] == "done"
        assert entry["implemented_at"] == "2026-01-01"


class TestFilterMarine:
    """Test domain filtering."""

    def test_filter_marine_pending(self, sample_ledger):
        mod = _import_batch_processor()
        result = mod.filter_standards(sample_ledger["standards"], domain="marine")
        # Should return DNV-OS-E301, DNV-RP-C205, DNV-OS-F101 (not done, not pipeline)
        ids = [s["id"] for s in result]
        assert "DNV-OS-E301" in ids
        assert "DNV-RP-C205" in ids
        assert "DNV-OS-F101" in ids
        assert "API-RP-2SK" not in ids   # already done
        assert "API-5L" not in ids        # pipeline domain


class TestBatchProgress:
    """Test batch progress tracking."""

    def test_progress_tracking(self, sample_ledger):
        mod = _import_batch_processor()
        candidates = mod.filter_standards(sample_ledger["standards"], domain="marine")
        progress = mod.BatchProgress(total=len(candidates))
        progress.mark_processed("DNV-OS-E301")
        assert progress.processed == 1
        assert progress.remaining == len(candidates) - 1
        assert "1/" in progress.summary()

    def test_progress_report_format(self, sample_ledger):
        mod = _import_batch_processor()
        candidates = mod.filter_standards(sample_ledger["standards"], domain="marine")
        progress = mod.BatchProgress(total=len(candidates))
        for c in candidates:
            progress.mark_processed(c["id"])
        report = progress.summary()
        assert f"{len(candidates)}/{len(candidates)}" in report


class TestDryRun:
    """Test dry-run mode does not write changes."""

    def test_dry_run_no_file_change(self, ledger_file):
        mod = _import_batch_processor()
        original_content = ledger_file.read_text()
        mod.run_batch(str(ledger_file), domain="marine", dry_run=True, limit=None)
        assert ledger_file.read_text() == original_content


class TestLedgerWriting:
    """Test YAML ledger writing."""

    def test_save_ledger_roundtrip(self, sample_ledger, tmp_path):
        mod = _import_batch_processor()
        out_path = tmp_path / "output.yaml"
        mod.save_ledger(sample_ledger, str(out_path))
        reloaded = mod.load_ledger(str(out_path))
        assert len(reloaded["standards"]) == len(sample_ledger["standards"])
        assert reloaded["total"] == sample_ledger["total"]


class TestLimitFlag:
    """Test --limit N flag behaviour."""

    def test_limit_caps_processing(self, ledger_file):
        mod = _import_batch_processor()
        result = mod.run_batch(str(ledger_file), domain="marine", dry_run=True, limit=1)
        assert result["processed_count"] == 1


class TestMetadataExtraction:
    """Test basic metadata extraction (file size, existence)."""

    def test_extract_metadata_existing_file(self, tmp_path):
        mod = _import_batch_processor()
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"fake pdf content " * 100)
        meta = mod.extract_metadata(str(dummy))
        assert meta["exists"] is True
        assert meta["file_size_bytes"] > 0

    def test_extract_metadata_missing_file(self):
        mod = _import_batch_processor()
        meta = mod.extract_metadata("/nonexistent/path/to/file.pdf")
        assert meta["exists"] is False
        assert meta["file_size_bytes"] == 0
