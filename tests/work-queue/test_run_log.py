"""Tests for run_log.py — event-sourced crash recovery for WRK stage pipeline.

TDD: Red → Green → Refactor for WRK-1187 Enhancement 1.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

# Import path setup
import sys
WORK_QUEUE_DIR = Path(__file__).parent.parent.parent / "scripts" / "work-queue"
if not WORK_QUEUE_DIR.exists():
    pytest.skip("legacy scripts/work-queue/ implementation is not present in this checkout", allow_module_level=True)
sys.path.insert(0, str(WORK_QUEUE_DIR))

from run_log import append_stage_event, read_completed_stages, should_skip_stage, hash_entry_files


class TestAppendStageEvent:
    """append_stage_event writes JSONL to run-log.jsonl."""

    def test_creates_file_if_missing(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done")
        assert log_path.exists()

    def test_appends_valid_jsonl(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done")
        append_stage_event(str(log_path), stage=11, status="done")
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            data = json.loads(line)
            assert "stage" in data
            assert "status" in data
            assert "ts" in data

    def test_records_entry_hash(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done", entry_hash="abc123")
        data = json.loads(log_path.read_text().strip())
        assert data["entry_hash"] == "abc123"


class TestReadCompletedStages:
    """read_completed_stages returns set of done stage numbers."""

    def test_empty_file(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        log_path.write_text("")
        assert read_completed_stages(str(log_path)) == set()

    def test_missing_file(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        assert read_completed_stages(str(log_path)) == set()

    def test_reads_done_stages(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=8, status="done")
        append_stage_event(str(log_path), stage=9, status="done")
        append_stage_event(str(log_path), stage=10, status="done")
        assert read_completed_stages(str(log_path)) == {8, 9, 10}

    def test_ignores_non_done_status(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=8, status="done")
        append_stage_event(str(log_path), stage=9, status="failed")
        assert read_completed_stages(str(log_path)) == {8}


class TestShouldSkipStage:
    """should_skip_stage checks if stage was already completed with same inputs."""

    def test_skip_when_done_and_hash_matches(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done", entry_hash="abc")
        assert should_skip_stage(str(log_path), stage=10, current_hash="abc") is True

    def test_no_skip_when_hash_differs(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done", entry_hash="abc")
        assert should_skip_stage(str(log_path), stage=10, current_hash="xyz") is False

    def test_no_skip_when_not_done(self, tmp_path):
        log_path = tmp_path / "run-log.jsonl"
        assert should_skip_stage(str(log_path), stage=10, current_hash="abc") is False

    def test_no_skip_when_no_hash(self, tmp_path):
        """Without content-addressed hashing, skip only checks done status."""
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done")
        assert should_skip_stage(str(log_path), stage=10) is True

    def test_no_skip_without_current_hash(self, tmp_path):
        """If log has hash but caller doesn't provide one, still skip (done is done)."""
        log_path = tmp_path / "run-log.jsonl"
        append_stage_event(str(log_path), stage=10, status="done", entry_hash="abc")
        assert should_skip_stage(str(log_path), stage=10) is True


class TestHashEntryFiles:
    """hash_entry_files produces deterministic hash of file contents."""

    def test_empty_list(self):
        assert hash_entry_files([]) == ""

    def test_deterministic(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h1 = hash_entry_files([str(f)])
        h2 = hash_entry_files([str(f)])
        assert h1 == h2
        assert len(h1) == 64  # sha256 hex

    def test_changes_on_content_change(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("version 1")
        h1 = hash_entry_files([str(f)])
        f.write_text("version 2")
        h2 = hash_entry_files([str(f)])
        assert h1 != h2

    def test_missing_file_skipped(self, tmp_path):
        f = tmp_path / "exists.txt"
        f.write_text("data")
        h1 = hash_entry_files([str(f)])
        h2 = hash_entry_files([str(f), str(tmp_path / "missing.txt")])
        assert h1 == h2  # missing file is skipped
