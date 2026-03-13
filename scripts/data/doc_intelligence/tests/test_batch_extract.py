"""TDD tests for batch extraction pipeline — queue.py + batch-extract.py."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Ensure repo root on PYTHONPATH
_repo_root = str(Path(__file__).resolve().parents[4])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from scripts.data.doc_intelligence.queue import (
    get_pending,
    get_stats,
    load_queue,
    mark_completed,
    mark_failed,
    save_queue,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_QUEUE = {
    "version": "1.0",
    "queue": {"name": "test-corpus", "created_at": "2026-03-13T00:00:00Z"},
    "documents": [
        {
            "path": "/tmp/doc1.pdf",
            "domain": "naval-architecture",
            "doc_ref": "DOC-001",
            "status": "pending",
            "error": None,
            "manifest_path": None,
            "processed_at": None,
        },
        {
            "path": "/tmp/doc2.pdf",
            "domain": "naval-architecture",
            "doc_ref": "DOC-002",
            "status": "completed",
            "error": None,
            "manifest_path": "/tmp/out/doc2.manifest.yaml",
            "processed_at": "2026-03-13T01:00:00Z",
        },
        {
            "path": "/tmp/doc3.pdf",
            "domain": "naval-architecture",
            "doc_ref": "DOC-003",
            "status": "failed",
            "error": "parse error",
            "manifest_path": None,
            "processed_at": None,
        },
    ],
    "settings": {
        "batch_size": 50,
        "rate_limit": 2.0,
        "output_dir": "data/doc-intelligence/manifests",
        "dry_run": False,
    },
}


@pytest.fixture
def queue_file(tmp_path):
    """Write a valid queue YAML and return its path."""
    p = tmp_path / "queue.yaml"
    p.write_text(yaml.dump(VALID_QUEUE, default_flow_style=False, sort_keys=False))
    return p


@pytest.fixture
def queue_data():
    """Return a deep copy of VALID_QUEUE."""
    import copy
    return copy.deepcopy(VALID_QUEUE)


# ===========================================================================
# Tests 1-8: queue.py
# ===========================================================================


class TestLoadQueue:
    def test_load_queue_valid(self, queue_file):
        """Test 1: Parses well-formed queue YAML."""
        q = load_queue(queue_file)
        assert q["version"] == "1.0"
        assert q["queue"]["name"] == "test-corpus"
        assert len(q["documents"]) == 3

    def test_load_queue_missing_file(self, tmp_path):
        """Test 2: Raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_queue(tmp_path / "nonexistent.yaml")

    def test_load_queue_invalid_yaml(self, tmp_path):
        """Test 3: Raises ValueError for malformed YAML."""
        bad = tmp_path / "bad.yaml"
        bad.write_text(": : invalid\n  - [broken")
        with pytest.raises(ValueError):
            load_queue(bad)


class TestGetPending:
    def test_get_pending_filters_completed(self, queue_data):
        """Test 4: Only returns docs with status=pending."""
        pending = get_pending(queue_data)
        assert len(pending) == 1
        assert pending[0]["doc_ref"] == "DOC-001"
        assert all(d["status"] == "pending" for d in pending)


class TestGetStats:
    def test_get_stats_counts(self, queue_data):
        """Test 5: Returns correct pending/completed/failed/total."""
        stats = get_stats(queue_data)
        assert stats["pending"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 1
        assert stats["total"] == 3


class TestMarkCompleted:
    def test_mark_completed_updates_fields(self):
        """Test 6: Sets status, manifest_path, processed_at."""
        doc = {
            "path": "/tmp/doc.pdf",
            "status": "processing",
            "error": None,
            "manifest_path": None,
            "processed_at": None,
        }
        mark_completed(doc, "/tmp/out/doc.manifest.yaml")
        assert doc["status"] == "completed"
        assert doc["manifest_path"] == "/tmp/out/doc.manifest.yaml"
        assert doc["processed_at"] is not None


class TestMarkFailed:
    def test_mark_failed_records_error(self):
        """Test 7: Sets status=failed and error message."""
        doc = {
            "path": "/tmp/doc.pdf",
            "status": "processing",
            "error": None,
            "manifest_path": None,
            "processed_at": None,
        }
        mark_failed(doc, "unsupported format")
        assert doc["status"] == "failed"
        assert doc["error"] == "unsupported format"
        assert doc["processed_at"] is not None


class TestSaveQueue:
    def test_save_queue_atomic_write(self, queue_data, tmp_path):
        """Test 8: Uses tmpfile + os.replace (no partial writes)."""
        out = tmp_path / "out-queue.yaml"
        with patch("os.replace", wraps=os.replace) as mock_replace:
            save_queue(queue_data, out)
            mock_replace.assert_called_once()
        loaded = yaml.safe_load(out.read_text())
        assert loaded["version"] == "1.0"
        assert len(loaded["documents"]) == 3


# ===========================================================================
# Tests 9-15: batch-extract.py (CLI integration)
# ===========================================================================

BATCH_SCRIPT = str(
    Path(__file__).resolve().parents[2] / "doc-intelligence" / "batch-extract.py"
)


def _make_queue(tmp_path, docs, settings=None):
    """Helper: write a queue YAML with given docs and return path."""
    q = {
        "version": "1.0",
        "queue": {"name": "test", "created_at": "2026-03-13T00:00:00Z"},
        "documents": docs,
        "settings": settings or {
            "batch_size": 50,
            "rate_limit": 0.0,
            "output_dir": str(tmp_path / "manifests"),
            "dry_run": False,
        },
    }
    p = tmp_path / "queue.yaml"
    p.write_text(yaml.dump(q, default_flow_style=False, sort_keys=False))
    return p


def _pending_doc(path="/tmp/test.pdf", ref="T-001"):
    return {
        "path": path,
        "domain": "test",
        "doc_ref": ref,
        "status": "pending",
        "error": None,
        "manifest_path": None,
        "processed_at": None,
    }


def _run_batch(args, env=None):
    """Run batch-extract.py and return CompletedProcess."""
    cmd = [sys.executable, BATCH_SCRIPT] + args
    return subprocess.run(cmd, capture_output=True, text=True, env=env or os.environ)


class TestBatchExtractCLI:
    def test_batch_extract_dry_run(self, tmp_path):
        """Test 9: Dry run processes nothing, prints summary."""
        qf = _make_queue(tmp_path, [_pending_doc()])
        result = _run_batch(["--queue", str(qf), "--dry-run"])
        assert result.returncode == 0
        assert "dry run" in result.stdout.lower() or "dry-run" in result.stdout.lower()
        # Queue should remain unchanged
        q = yaml.safe_load(qf.read_text())
        assert q["documents"][0]["status"] == "pending"

    def test_batch_extract_rate_limit(self, tmp_path):
        """Test 10: Enforces delay between docs."""
        docs = [_pending_doc(f"/tmp/d{i}.pdf", f"T-{i:03d}") for i in range(3)]
        qf = _make_queue(tmp_path, docs, {
            "batch_size": 50,
            "rate_limit": 0.3,
            "output_dir": str(tmp_path / "manifests"),
            "dry_run": False,
        })
        start = time.monotonic()
        # Will fail extraction (files don't exist) but rate limit still applies
        _run_batch(["--queue", str(qf), "--rate-limit", "0.3"])
        elapsed = time.monotonic() - start
        # 3 docs with 0.3s rate limit = at least 0.6s total delay
        assert elapsed >= 0.5

    def test_batch_extract_checkpoint(self, tmp_path):
        """Test 11: Saves queue every batch_size docs."""
        docs = [_pending_doc(f"/tmp/d{i}.pdf", f"T-{i:03d}") for i in range(5)]
        qf = _make_queue(tmp_path, docs)
        _run_batch(["--queue", str(qf), "--batch-size", "2"])
        # After run, queue file should reflect processed state
        q = yaml.safe_load(qf.read_text())
        processed = [d for d in q["documents"] if d["status"] != "pending"]
        assert len(processed) == 5

    def test_batch_extract_resume(self, tmp_path):
        """Test 12: Skips completed docs on resume."""
        docs = [
            {**_pending_doc("/tmp/d1.pdf", "T-001"), "status": "completed",
             "manifest_path": "/tmp/m.yaml", "processed_at": "2026-03-13T00:00:00Z"},
            _pending_doc("/tmp/d2.pdf", "T-002"),
        ]
        qf = _make_queue(tmp_path, docs)
        _run_batch(["--queue", str(qf), "--resume"])
        q = yaml.safe_load(qf.read_text())
        # First doc should remain completed (not reprocessed)
        assert q["documents"][0]["status"] == "completed"
        # Second doc should have been attempted
        assert q["documents"][1]["status"] != "pending"

    def test_batch_extract_failure_tracking(self, tmp_path):
        """Test 13: Failed docs get error recorded."""
        qf = _make_queue(tmp_path, [_pending_doc("/tmp/nonexistent.pdf")])
        _run_batch(["--queue", str(qf)])
        q = yaml.safe_load(qf.read_text())
        assert q["documents"][0]["status"] == "failed"
        assert q["documents"][0]["error"] is not None

    def test_batch_extract_exit_codes(self, tmp_path):
        """Test 14: Correct exit codes per scenario."""
        # Exit 2: missing queue file
        result = _run_batch(["--queue", str(tmp_path / "missing.yaml")])
        assert result.returncode == 2

        # Exit 1: partial failure (file doesn't exist)
        qf = _make_queue(tmp_path, [_pending_doc("/tmp/nonexistent.pdf")])
        result = _run_batch(["--queue", str(qf)])
        assert result.returncode == 1

    def test_batch_extract_all_completed(self, tmp_path):
        """Test 15: Exit 3 when no pending docs."""
        docs = [{
            **_pending_doc(), "status": "completed",
            "manifest_path": "/tmp/m.yaml", "processed_at": "2026-03-13T00:00:00Z",
        }]
        qf = _make_queue(tmp_path, docs)
        result = _run_batch(["--queue", str(qf)])
        assert result.returncode == 3
