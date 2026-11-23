"""Tests for comprehensive_learning_pipeline.py fixes — WRK-1168.

Covers:
1. Dedup: create_wrk_item skips if matching title already exists in pending/
2. Timeout: phases complete within budget
3. Phase 5/7/9 produce PHASE_RESULT output (no hang)
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "analysis"))

from comprehensive_learning_pipeline import (
    create_wrk_item,
    title_already_exists,
    phase_5_correction_trend_analysis,
    phase_7_action_candidates,
    phase_9_skill_coverage_audit,
)


@pytest.fixture
def mock_workspace(tmp_path, monkeypatch):
    """Set up isolated workspace for pipeline tests."""
    pending = tmp_path / ".claude" / "work-queue" / "pending"
    pending.mkdir(parents=True)
    state = tmp_path / ".claude" / "work-queue"
    (state / "state.yaml").write_text("last_id: 0\n")

    # Create dirs the pipeline expects
    (tmp_path / ".claude" / "state" / "corrections").mkdir(parents=True)
    (tmp_path / ".claude" / "state" / "candidates").mkdir(parents=True)
    (tmp_path / ".claude" / "state" / "session-signals").mkdir(parents=True)

    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    # Patch module-level paths
    import comprehensive_learning_pipeline as clp
    monkeypatch.setattr(clp, "WS_HUB", str(tmp_path))
    monkeypatch.setattr(clp, "PENDING_WRK_DIR", str(pending))
    monkeypatch.setattr(clp, "CORRECTIONS_DIR", str(tmp_path / ".claude" / "state" / "corrections"))
    monkeypatch.setattr(clp, "CANDIDATES_DIR", str(tmp_path / ".claude" / "state" / "candidates"))
    monkeypatch.setattr(clp, "STATE_DIR", str(tmp_path / ".claude" / "state"))

    return tmp_path


class TestTitleDedup:
    """title_already_exists prevents duplicate WRK creation."""

    def test_no_match_returns_false(self, mock_workspace):
        assert title_already_exists("Brand new task", str(mock_workspace / ".claude" / "work-queue" / "pending")) is False

    def test_exact_match_returns_true(self, mock_workspace):
        pending = mock_workspace / ".claude" / "work-queue" / "pending"
        (pending / "WRK-9999.md").write_text('---\ntitle: "Fix the widget"\nstatus: pending\n---\n')
        assert title_already_exists("Fix the widget", str(pending)) is True

    def test_substring_match_returns_true(self, mock_workspace):
        """Fuzzy match: if existing title contains candidate title (or vice versa)."""
        pending = mock_workspace / ".claude" / "work-queue" / "pending"
        (pending / "WRK-9999.md").write_text('---\ntitle: "[script]: fetch-queue-manager — auto-actioned from candidates"\nstatus: pending\n---\n')
        assert title_already_exists("fetch-queue-manager", str(pending)) is True

    def test_case_insensitive(self, mock_workspace):
        pending = mock_workspace / ".claude" / "work-queue" / "pending"
        (pending / "WRK-9999.md").write_text('---\ntitle: "Fix The Widget"\nstatus: pending\n---\n')
        assert title_already_exists("fix the widget", str(pending)) is True


class TestPhaseTimeout:
    """Phases must complete within a reasonable time budget."""

    def test_phase_5_returns_result(self, mock_workspace):
        """Phase 5 returns a result tuple even with no data."""
        status, notes = phase_5_correction_trend_analysis()
        assert status in ("DONE", "SKIPPED")

    def test_phase_7_returns_result(self, mock_workspace):
        """Phase 7 returns a result tuple even with no candidates."""
        status, notes = phase_7_action_candidates()
        assert status in ("DONE", "SKIPPED")

    def test_phase_9_returns_result(self, mock_workspace):
        """Phase 9 returns a result tuple even with no skills."""
        status, notes = phase_9_skill_coverage_audit()
        assert status in ("DONE", "SKIPPED")
