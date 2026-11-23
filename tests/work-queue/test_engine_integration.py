"""End-to-end integration tests for WRK-1187 engine enhancements.

Runs 5 simulated WRK items through the stage pipeline to verify:
1. run-log.jsonl captures every stage exit
2. Transition table validation rejects illegal transitions
3. Content-addressed skipping works on resume
4. Crash recovery skips already-completed stages
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

WORK_QUEUE_DIR = Path(__file__).parent.parent.parent / "scripts" / "work-queue"
if not WORK_QUEUE_DIR.exists():
    pytest.skip("legacy scripts/work-queue/ implementation is not present in this checkout", allow_module_level=True)

# Import path setup
sys.path.insert(0, str(WORK_QUEUE_DIR))

from run_log import append_stage_event, read_completed_stages, should_skip_stage, hash_entry_files
from generate_transition_table import load_stage_contracts, build_transition_table, validate_transition

STAGES_DIR = str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "workspace-hub" / "stages")


@pytest.fixture
def wrk_dir(tmp_path):
    """Create a minimal WRK assets directory."""
    assets = tmp_path / "assets" / "WRK-9001"
    assets.mkdir(parents=True)
    (assets / "evidence").mkdir()
    return assets


# ── Suite 1: Run log captures stage exits ──

class TestRunLogCapture:
    """Verify run-log.jsonl records each stage exit."""

    def test_stages_recorded_sequentially(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        for stage in [1, 2, 3, 4]:
            append_stage_event(log, stage, "done")

        completed = read_completed_stages(log)
        assert completed == {1, 2, 3, 4}

    def test_jsonl_format_valid(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        for stage in [1, 2, 3]:
            append_stage_event(log, stage, "done")

        lines = Path(log).read_text().strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            event = json.loads(line)
            assert event["status"] == "done"
            assert "ts" in event

    def test_failed_stage_not_in_completed(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        append_stage_event(log, 1, "done")
        append_stage_event(log, 2, "failed")
        append_stage_event(log, 3, "done")
        assert read_completed_stages(log) == {1, 3}


# ── Suite 2: Crash recovery ──

class TestCrashRecovery:
    """Simulate crash and resume — completed stages are skipped."""

    def test_resume_skips_completed_stages(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        # First run: complete stages 1-3
        for s in [1, 2, 3]:
            append_stage_event(log, s, "done")

        # Resume: stages 1-3 skip, 4-5 don't
        assert should_skip_stage(log, 1) is True
        assert should_skip_stage(log, 2) is True
        assert should_skip_stage(log, 3) is True
        assert should_skip_stage(log, 4) is False
        assert should_skip_stage(log, 5) is False

    def test_resume_from_empty_log(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        # No log → nothing to skip
        assert should_skip_stage(log, 1) is False


# ── Suite 3: Content-addressed skipping ──

class TestContentAddressedSkipping:
    """Skip stages only when input files haven't changed."""

    def test_same_inputs_skip(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        entry_file = wrk_dir / "input.txt"
        entry_file.write_text("version 1")
        h = hash_entry_files([str(entry_file)])

        append_stage_event(log, 10, "done", entry_hash=h)
        assert should_skip_stage(log, 10, current_hash=h) is True

    def test_changed_inputs_no_skip(self, wrk_dir):
        log = str(wrk_dir / "run-log.jsonl")
        entry_file = wrk_dir / "input.txt"
        entry_file.write_text("version 1")
        h1 = hash_entry_files([str(entry_file)])

        append_stage_event(log, 10, "done", entry_hash=h1)

        # Change input
        entry_file.write_text("version 2")
        h2 = hash_entry_files([str(entry_file)])
        assert should_skip_stage(log, 10, current_hash=h2) is False

    def test_hash_is_deterministic(self, wrk_dir):
        f1 = wrk_dir / "a.txt"
        f2 = wrk_dir / "b.txt"
        f1.write_text("alpha")
        f2.write_text("beta")
        h1 = hash_entry_files([str(f1), str(f2)])
        h2 = hash_entry_files([str(f1), str(f2)])
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex


# ── Suite 4: Transition table validation ──

class TestTransitionValidation:
    """Transition table enforces sequential stage progression."""

    @pytest.fixture
    def table(self):
        contracts = load_stage_contracts(STAGES_DIR)
        return build_transition_table(contracts)

    def test_sequential_allowed(self, table):
        assert validate_transition(table, 1, 2) is True
        assert validate_transition(table, 5, 6) is True
        assert validate_transition(table, 19, 20) is True

    def test_skip_blocked(self, table):
        assert validate_transition(table, 1, 5) is False
        assert validate_transition(table, 3, 10) is False
        assert validate_transition(table, 1, 20) is False

    def test_backward_blocked(self, table):
        assert validate_transition(table, 10, 5) is False
        assert validate_transition(table, 20, 1) is False

    def test_19_transitions_total(self, table):
        assert len(table) == 19

    def test_human_gates_marked(self, table):
        human_stages = {t["from_stage"] for t in table if t["human_gate"]}
        assert {5, 7, 17}.issubset(human_stages)


# ── Suite 5: Pipeline of 5 WRK items ──

class TestFiveItemPipeline:
    """Run 5 WRK items through stages 1-8 to verify full pipeline."""

    ITEMS = [
        ("9002", "Fix widget color"),
        ("9003", "Add tooltip"),
        ("9004", "Update docs"),
        ("9005", "Refactor util"),
        ("9006", "Bump version"),
    ]

    @pytest.mark.parametrize("wrk_id,title", ITEMS)
    def test_item_completes_stages_1_to_8(self, tmp_path, wrk_id, title):
        """Each WRK item runs through stages 1-8, all recorded in run log."""
        assets = tmp_path / f"WRK-{wrk_id}"
        assets.mkdir(parents=True)
        log = str(assets / "run-log.jsonl")

        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)

        # Run stages 1-8 sequentially
        prev_stage = 0
        for stage in range(1, 9):
            # Check transition is legal (except first stage)
            if prev_stage > 0:
                assert validate_transition(table, prev_stage, stage), \
                    f"Transition {prev_stage}→{stage} should be legal"

            # Check if stage should be skipped (none should on first run)
            assert not should_skip_stage(log, stage), \
                f"Stage {stage} should NOT be skipped on first run"

            # Execute stage (simulated)
            append_stage_event(log, stage, "done")
            prev_stage = stage

        # Verify all 8 stages completed
        completed = read_completed_stages(log)
        assert completed == {1, 2, 3, 4, 5, 6, 7, 8}

    @pytest.mark.parametrize("wrk_id,title", ITEMS)
    def test_item_resume_skips_completed(self, tmp_path, wrk_id, title):
        """After completing 1-8, resume skips all 8 and continues from 9."""
        assets = tmp_path / f"WRK-{wrk_id}"
        assets.mkdir(parents=True)
        log = str(assets / "run-log.jsonl")

        # First run: stages 1-8
        for stage in range(1, 9):
            append_stage_event(log, stage, "done")

        # Resume: stages 1-8 should skip, 9 should not
        for stage in range(1, 9):
            assert should_skip_stage(log, stage), \
                f"Stage {stage} should be skipped on resume"
        assert not should_skip_stage(log, 9), \
            "Stage 9 should NOT be skipped (not yet done)"
