"""Tests for urgency-score.py — WRK-1309.

Run: uv run --no-project python -m pytest tests/work-queue/test_urgency_score.py -v
"""
import json
import os
import sys
import textwrap

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
WORK_QUEUE_DIR = os.path.join(REPO, "scripts", "work-queue")
if not os.path.isdir(WORK_QUEUE_DIR):
    pytest.skip("legacy scripts/work-queue/ implementation is not present in this checkout", allow_module_level=True)
sys.path.insert(0, WORK_QUEUE_DIR)

from urgency_score import (  # noqa: E402
    compute_score, parse_weights, score_age, score_blocked,
    score_blocking_count, score_checkpoint, score_due,
    score_priority, score_all, get_field, parse_list_field,
)

from datetime import datetime, timezone, timedelta  # noqa: E402

WEIGHTS = {
    "priority": {"high": 6.0, "medium": 3.9, "low": 1.8},
    "blocking_count": 8.0,
    "age_factor": 2.0,
    "blocked_penalty": -5.0,
    "has_checkpoint": 4.0,
    "due_proximity": 12.0,
}


def _wrk_file(d, wrk_id, **fields):
    """Create a minimal WRK .md file in directory d."""
    lines = ["---"]
    lines.append(f"id: {wrk_id}")
    for k, v in fields.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    path = os.path.join(d, f"{wrk_id}.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ── Priority ──────────────────────────────────────────────────────────

class TestPriorityScoring:
    def test_high(self):
        assert score_priority("high", WEIGHTS) == 6.0

    def test_medium(self):
        assert score_priority("medium", WEIGHTS) == 3.9

    def test_low(self):
        assert score_priority("low", WEIGHTS) == 1.8

    def test_missing(self):
        assert score_priority("", WEIGHTS) == 0.0

    def test_unknown(self):
        assert score_priority("critical", WEIGHTS) == 0.0


# ── Age ───────────────────────────────────────────────────────────────

class TestAgeScoring:
    def test_zero_days(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        assert score_age("2026-03-17", WEIGHTS, now=now) == 0.0

    def test_fifteen_days(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        # 15 days → min(15/30, 10) * 2.0 / 10 = 0.5 * 0.2 = 0.1
        result = score_age("2026-03-02", WEIGHTS, now=now)
        assert result == pytest.approx(0.1, abs=0.05)

    def test_thirty_days_cap(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        # 30 days → min(30/30, 10) * 2.0 / 10 = 1.0 * 0.2 = 0.2
        result = score_age("2026-02-15", WEIGHTS, now=now)
        assert result == pytest.approx(0.2, abs=0.01)

    def test_three_hundred_days(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        # 300 days → min(300/30, 10) = 10 → 10 * 2.0 / 10 = 2.0
        result = score_age("2025-05-22", WEIGHTS, now=now)
        assert result == pytest.approx(2.0, abs=0.1)

    def test_missing_date(self):
        assert score_age("", WEIGHTS) == 0.0

    def test_with_timezone(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        result = score_age("2026-03-02 00:00:00+00:00", WEIGHTS, now=now)
        assert result == pytest.approx(0.1, abs=0.05)


# ── Blocking count ────────────────────────────────────────────────────

class TestBlockingCount:
    def test_blocking_two_items(self):
        files = [
            ("a.md", "blocked_by: [WRK-100]"),
            ("b.md", "blocked_by: [WRK-100, WRK-200]"),
            ("c.md", "blocked_by: [WRK-200]"),
        ]
        result = score_blocking_count("WRK-100", files, WEIGHTS)
        assert result == 16.0  # 2 items * 8.0

    def test_blocking_none(self):
        files = [
            ("a.md", "blocked_by: [WRK-200]"),
        ]
        result = score_blocking_count("WRK-100", files, WEIGHTS)
        assert result == 0.0

    def test_blocking_empty_list(self):
        files = [("a.md", "blocked_by: []")]
        result = score_blocking_count("WRK-100", files, WEIGHTS)
        assert result == 0.0


# ── Blocked penalty ──────────────────────────────────────────────────

class TestBlockedPenalty:
    def test_unresolved_blocker(self, tmp_path):
        archive = tmp_path / "archive"
        archive.mkdir()
        result = score_blocked(
            ["WRK-999"], WEIGHTS,
            archive_dirs=[str(archive)])
        assert result == -5.0

    def test_resolved_blocker(self, tmp_path):
        archive = tmp_path / "archive"
        archive.mkdir()
        (archive / "WRK-999.md").write_text("archived")
        result = score_blocked(
            ["WRK-999"], WEIGHTS,
            archive_dirs=[str(archive)])
        assert result == 0.0

    def test_no_blockers(self):
        assert score_blocked([], WEIGHTS) == 0.0


# ── Checkpoint bonus ─────────────────────────────────────────────────

class TestCheckpointBonus:
    def test_with_checkpoint(self, tmp_path):
        assets = tmp_path / "assets" / "WRK-100"
        assets.mkdir(parents=True)
        (assets / "checkpoint.yaml").write_text("current_stage: 3")
        result = score_checkpoint("WRK-100", WEIGHTS, str(tmp_path))
        assert result == 4.0

    def test_without_checkpoint(self, tmp_path):
        result = score_checkpoint("WRK-100", WEIGHTS, str(tmp_path))
        assert result == 0.0


# ── Due proximity ────────────────────────────────────────────────────

class TestDueProximity:
    def test_overdue(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        result = score_due("2026-03-10", WEIGHTS, now=now)
        assert result == 12.0

    def test_fifteen_days_out(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        # 15 days out → 12 * (30-15)/30 = 6.0
        result = score_due("2026-04-01", WEIGHTS, now=now)
        assert result == pytest.approx(6.0, abs=0.1)

    def test_thirty_plus_days(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        result = score_due("2026-04-20", WEIGHTS, now=now)
        assert result == 0.0

    def test_no_due_date(self):
        assert score_due("", WEIGHTS) == 0.0

    def test_today(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        result = score_due("2026-03-17", WEIGHTS, now=now)
        assert result == 12.0


# ── Overall score ────────────────────────────────────────────────────

class TestOverallScore:
    def test_known_inputs(self, tmp_path):
        """High priority, 30-day-old, blocking 1 item, no blockers,
        with checkpoint, no due date."""
        pending = tmp_path / "pending"
        pending.mkdir()
        _wrk_file(str(pending), "WRK-100",
                  priority="high",
                  created_at="2026-02-15 00:00:00+00:00",
                  status="pending")
        _wrk_file(str(pending), "WRK-200",
                  priority="medium",
                  created_at="2026-03-15",
                  status="pending",
                  **{"blocked_by": "[WRK-100]"})
        # Create checkpoint for WRK-100
        cp_dir = tmp_path / "assets" / "WRK-100"
        cp_dir.mkdir(parents=True)
        (cp_dir / "checkpoint.yaml").write_text("current_stage: 5")

        all_files = []
        for fname in os.listdir(str(pending)):
            p = os.path.join(str(pending), fname)
            with open(p) as f:
                all_files.append((p, f.read()))

        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        total, bd = compute_score(
            "WRK-100", all_files[0][1] if "WRK-100" in all_files[0][0]
            else all_files[1][1],
            WEIGHTS, all_files, str(tmp_path), now=now)

        assert bd["priority"] == 6.0
        assert bd["blocking"] == 8.0  # blocks WRK-200
        assert bd["checkpoint"] == 4.0
        assert bd["blocked"] == 0.0
        assert total == pytest.approx(
            6.0 + 8.0 + 4.0 + bd["age"] + bd["due"], abs=0.1)


# ── score_all sorting ────────────────────────────────────────────────

class TestScoreAllSorting:
    def test_highest_first(self, tmp_path):
        pending = tmp_path / "pending"
        pending.mkdir()
        _wrk_file(str(pending), "WRK-001",
                  priority="low", status="pending",
                  created_at="2026-03-17")
        _wrk_file(str(pending), "WRK-002",
                  priority="high", status="pending",
                  created_at="2026-03-17")
        _wrk_file(str(pending), "WRK-003",
                  priority="medium", status="pending",
                  created_at="2026-03-17")

        results = score_all(str(tmp_path))
        ids = [r["id"] for r in results]
        assert ids[0] == "WRK-002"  # high first
        assert ids[1] == "WRK-003"  # medium second
        assert ids[2] == "WRK-001"  # low last


# ── Field parsing ────────────────────────────────────────────────────

class TestFieldParsing:
    def test_get_field(self):
        text = "id: WRK-100\npriority: high\n"
        assert get_field(text, "id") == "WRK-100"
        assert get_field(text, "priority") == "high"
        assert get_field(text, "missing") == ""

    def test_parse_list_field(self):
        text = "blocked_by: [WRK-100, WRK-200]\n"
        assert parse_list_field(text, "blocked_by") == [
            "WRK-100", "WRK-200"]

    def test_parse_empty_list(self):
        text = "blocked_by: []\n"
        assert parse_list_field(text, "blocked_by") == []


# ── Weights parsing ─────────────────────────────────────────────────

class TestWeightsParsing:
    def test_parse_weights_file(self, tmp_path):
        wf = tmp_path / "weights.yaml"
        wf.write_text(textwrap.dedent("""\
            priority:
              high: 7.0
              medium: 4.0
              low: 2.0
            blocking_count: 9.0
            age_factor: 3.0
            blocked_penalty: -6.0
            has_checkpoint: 5.0
            due_proximity: 15.0
        """))
        w = parse_weights(str(wf))
        assert w["priority"]["high"] == 7.0
        assert w["blocking_count"] == 9.0
        assert w["blocked_penalty"] == -6.0

    def test_missing_file_returns_defaults(self):
        w = parse_weights("/nonexistent/path.yaml")
        assert w["priority"]["high"] == 6.0
        assert w["blocking_count"] == 8.0
