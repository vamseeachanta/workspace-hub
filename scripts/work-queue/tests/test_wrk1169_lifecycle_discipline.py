"""
test_wrk1169_lifecycle_discipline.py — WRK-1169 AC verification.

Tests for:
  - _update_stage_ev() helper in exit_stage.py and start_stage.py
  - _stage1_pending_or_working_guard() in start_stage.py
  - _stage_progression_guard() in start_stage.py

Run with:
  uv run --no-project python -m pytest scripts/work-queue/tests/test_wrk1169_lifecycle_discipline.py -v
"""
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

from start_stage import (
    _stage1_pending_or_working_guard,
    _stage_progression_guard,
    _update_stage_ev,
)


# ── _stage1_pending_or_working_guard ─────────────────────────────────────────


def test_pending_or_working_guard_accepts_pending(tmp_path):
    """Stage 1 guard accepts item in pending/."""
    queue = tmp_path / "work-queue"
    (queue / "pending").mkdir(parents=True)
    (queue / "working").mkdir()
    (queue / "pending" / "WRK-100.md").write_text("id: WRK-100\n")
    _stage1_pending_or_working_guard("WRK-100", str(queue))  # must not raise


def test_pending_or_working_guard_accepts_working(tmp_path):
    """Stage 1 guard accepts item in working/."""
    queue = tmp_path / "work-queue"
    (queue / "pending").mkdir(parents=True)
    (queue / "working").mkdir()
    (queue / "working" / "WRK-100.md").write_text("id: WRK-100\n")
    _stage1_pending_or_working_guard("WRK-100", str(queue))  # must not raise


def test_pending_or_working_guard_blocks_missing(tmp_path):
    """Stage 1 guard exits 1 when item is in neither pending/ nor working/."""
    queue = tmp_path / "work-queue"
    (queue / "pending").mkdir(parents=True)
    (queue / "working").mkdir()
    with pytest.raises(SystemExit) as exc_info:
        _stage1_pending_or_working_guard("WRK-100", str(queue))
    assert exc_info.value.code == 1


# ── _stage_progression_guard ─────────────────────────────────────────────────


def _write_stage_evidence(assets_dir, wrk_id, stages):
    """Helper to write a stage-evidence.yaml with given stage entries."""
    ev_dir = assets_dir / wrk_id / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    lines = ["stages:"]
    for entry in stages:
        lines.append(f"  - order: {entry['order']}")
        lines.append(f"    status: {entry['status']}")
    (ev_dir / "stage-evidence.yaml").write_text("\n".join(lines) + "\n")


def test_progression_guard_allows_stage1(tmp_path):
    """Stage 1 has no prerequisite — always passes."""
    _stage_progression_guard("WRK-100", 1, str(tmp_path))  # must not raise


def test_progression_guard_allows_when_prev_done(tmp_path):
    """Stage 3 allowed when stage 2 is done."""
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    _write_stage_evidence(assets, "WRK-100", [
        {"order": 1, "status": "done"},
        {"order": 2, "status": "done"},
    ])
    _stage_progression_guard("WRK-100", 3, str(tmp_path))  # must not raise


def test_progression_guard_blocks_when_prev_in_progress(tmp_path):
    """Stage 3 blocked when stage 2 is still in_progress."""
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    _write_stage_evidence(assets, "WRK-100", [
        {"order": 1, "status": "done"},
        {"order": 2, "status": "in_progress"},
    ])
    with pytest.raises(SystemExit) as exc_info:
        _stage_progression_guard("WRK-100", 3, str(tmp_path))
    assert exc_info.value.code == 1


def test_progression_guard_blocks_when_prev_pending(tmp_path):
    """Stage 5 blocked when stage 4 is pending."""
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    _write_stage_evidence(assets, "WRK-100", [
        {"order": 1, "status": "done"},
        {"order": 2, "status": "done"},
        {"order": 3, "status": "done"},
        {"order": 4, "status": "pending"},
    ])
    with pytest.raises(SystemExit) as exc_info:
        _stage_progression_guard("WRK-100", 5, str(tmp_path))
    assert exc_info.value.code == 1


def test_progression_guard_allows_when_prev_na(tmp_path):
    """Stage 3 allowed when stage 2 is n/a."""
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    _write_stage_evidence(assets, "WRK-100", [
        {"order": 1, "status": "done"},
        {"order": 2, "status": "n/a"},
    ])
    _stage_progression_guard("WRK-100", 3, str(tmp_path))  # must not raise


def test_progression_guard_allows_when_no_evidence_file(tmp_path):
    """Backcompat: no stage-evidence.yaml means no blocking."""
    _stage_progression_guard("WRK-100", 5, str(tmp_path))  # must not raise


def test_progression_guard_allows_when_prev_stage_not_in_evidence(tmp_path):
    """If previous stage entry is missing from evidence, allow (backcompat)."""
    assets = tmp_path / ".claude" / "work-queue" / "assets"
    _write_stage_evidence(assets, "WRK-100", [
        {"order": 1, "status": "done"},
    ])
    # Stage 3 — stage 2 not in evidence at all
    _stage_progression_guard("WRK-100", 3, str(tmp_path))  # must not raise


# ── _update_stage_ev (smoke test — verifies subprocess call format) ──────────


def test_update_stage_ev_noop_when_script_missing(tmp_path):
    """_update_stage_ev does not crash when update-stage-evidence.py is absent."""
    _update_stage_ev("WRK-100", 3, "done", str(tmp_path))  # must not raise
