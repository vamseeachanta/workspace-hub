"""Tests for queue health reporting.

ABOUTME: Validates queue-health.sh companion logic — counts pending/completed/
failed jobs, reports timing stats, and formats health summaries.
All filesystem operations use temp directories.
"""
from __future__ import annotations

import textwrap
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_HEALTH_SCRIPT = REPO_ROOT / "scripts" / "solver" / "queue-health.sh"


# ---------------------------------------------------------------------------
# Queue health reporting logic (mirrors queue-health.sh)
# ---------------------------------------------------------------------------

def get_queue_health(queue_root: Path) -> dict:
    """Compute queue health stats from queue directory structure.

    Returns dict with:
      pending_count, completed_count, failed_count, total_processed,
      last_completed_at, oldest_pending_age_hours, health_status
    """
    pending_dir = queue_root / "pending"
    completed_dir = queue_root / "completed"
    failed_dir = queue_root / "failed"

    # Count pending jobs
    pending_files = []
    if pending_dir.exists():
        pending_files = [f for f in pending_dir.glob("*.yaml") if f.name != ".gitkeep"]
    pending_count = len(pending_files)

    # Count completed jobs
    completed_count = 0
    last_completed_at = None
    if completed_dir.exists():
        for job_dir in completed_dir.iterdir():
            if job_dir.is_dir():
                result = job_dir / "result.yaml"
                if result.exists():
                    completed_count += 1
                    try:
                        with open(result) as f:
                            data = yaml.safe_load(f)
                        ts = data.get("processed_at", "")
                        if ts and (last_completed_at is None or ts > last_completed_at):
                            last_completed_at = ts
                    except Exception:
                        pass

    # Count failed jobs
    failed_count = 0
    if failed_dir.exists():
        for job_dir in failed_dir.iterdir():
            if job_dir.is_dir():
                failed_count += 1

    # Compute oldest pending age
    oldest_pending_age_hours = 0.0
    now = datetime.now(timezone.utc)
    if pending_files:
        # Extract timestamp from filename: YYYYMMDDTHHMMSSZ-name.yaml
        for pf in pending_files:
            try:
                ts_str = pf.stem.split("-")[0]  # e.g. "20260401T120000Z"
                ts = datetime.strptime(ts_str, "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc
                )
                age = (now - ts).total_seconds() / 3600
                if age > oldest_pending_age_hours:
                    oldest_pending_age_hours = age
            except (ValueError, IndexError):
                pass

    # Determine health status
    if failed_count > 0 and pending_count > 5:
        health_status = "CRITICAL"
    elif failed_count > 0:
        health_status = "WARNING"
    elif pending_count > 10:
        health_status = "WARNING"
    else:
        health_status = "HEALTHY"

    return {
        "pending_count": pending_count,
        "completed_count": completed_count,
        "failed_count": failed_count,
        "total_processed": completed_count + failed_count,
        "last_completed_at": last_completed_at,
        "oldest_pending_age_hours": round(oldest_pending_age_hours, 1),
        "health_status": health_status,
    }


def format_health_report(health: dict) -> str:
    """Format queue health as a human-readable report string."""
    lines = [
        "=== Solver Queue Health ===",
        f"Status:           {health['health_status']}",
        f"Pending jobs:     {health['pending_count']}",
        f"Completed jobs:   {health['completed_count']}",
        f"Failed jobs:      {health['failed_count']}",
        f"Total processed:  {health['total_processed']}",
    ]
    if health["last_completed_at"]:
        lines.append(f"Last completed:   {health['last_completed_at']}")
    else:
        lines.append("Last completed:   N/A")
    if health["oldest_pending_age_hours"] > 0:
        lines.append(
            f"Oldest pending:   {health['oldest_pending_age_hours']}h ago"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def healthy_queue(tmp_path: Path) -> Path:
    """Queue with 0 pending, 2 completed, 0 failed."""
    q = tmp_path / "queue"
    (q / "pending").mkdir(parents=True)
    (q / "completed").mkdir(parents=True)
    (q / "failed").mkdir(parents=True)

    for i, ts in enumerate(["2026-04-01T10:00:00Z", "2026-04-01T12:00:00Z"]):
        job = q / "completed" / f"job{i}"
        job.mkdir()
        (job / "result.yaml").write_text(
            f"status: completed\nprocessed_at: {ts}\nsolver: orcawave\n"
        )
    return q


@pytest.fixture
def unhealthy_queue(tmp_path: Path) -> Path:
    """Queue with pending jobs and failures."""
    q = tmp_path / "queue"
    (q / "pending").mkdir(parents=True)
    (q / "completed").mkdir(parents=True)
    (q / "failed").mkdir(parents=True)

    # 3 pending jobs
    for i in range(3):
        (q / "pending" / f"20260401T{10+i:02d}0000Z-job{i}.yaml").write_text(
            f"solver: orcawave\ninput_file: test{i}.owd\n"
        )

    # 1 completed
    job = q / "completed" / "job0"
    job.mkdir()
    (job / "result.yaml").write_text(
        "status: completed\nprocessed_at: 2026-04-01T09:00:00Z\n"
    )

    # 2 failed
    for i in range(2):
        fail = q / "failed" / f"fail{i}"
        fail.mkdir()
        (fail / "result.yaml").write_text("status: failed\nerror: timeout\n")

    return q


@pytest.fixture
def empty_queue(tmp_path: Path) -> Path:
    """Completely empty queue."""
    q = tmp_path / "queue"
    (q / "pending").mkdir(parents=True)
    (q / "completed").mkdir(parents=True)
    (q / "failed").mkdir(parents=True)
    return q


# ---------------------------------------------------------------------------
# Tests: Queue health stats
# ---------------------------------------------------------------------------

class TestQueueHealthStats:
    """Test queue health stat computation."""

    def test_healthy_queue_counts(self, healthy_queue: Path):
        """Healthy queue reports correct counts."""
        health = get_queue_health(healthy_queue)
        assert health["pending_count"] == 0
        assert health["completed_count"] == 2
        assert health["failed_count"] == 0
        assert health["total_processed"] == 2

    def test_healthy_queue_status(self, healthy_queue: Path):
        """Queue with no failures and few pending is HEALTHY."""
        health = get_queue_health(healthy_queue)
        assert health["health_status"] == "HEALTHY"

    def test_unhealthy_queue_counts(self, unhealthy_queue: Path):
        """Unhealthy queue reports correct counts."""
        health = get_queue_health(unhealthy_queue)
        assert health["pending_count"] == 3
        assert health["completed_count"] == 1
        assert health["failed_count"] == 2

    def test_unhealthy_queue_status(self, unhealthy_queue: Path):
        """Queue with failures triggers WARNING."""
        health = get_queue_health(unhealthy_queue)
        assert health["health_status"] == "WARNING"

    def test_empty_queue(self, empty_queue: Path):
        """Empty queue is HEALTHY with all-zero counts."""
        health = get_queue_health(empty_queue)
        assert health["pending_count"] == 0
        assert health["completed_count"] == 0
        assert health["failed_count"] == 0
        assert health["health_status"] == "HEALTHY"


class TestLastCompletedTimestamp:
    """Test last completed timestamp tracking."""

    def test_last_completed_is_most_recent(self, healthy_queue: Path):
        """Last completed is the most recent timestamp."""
        health = get_queue_health(healthy_queue)
        # YAML safe_load may parse timestamps as datetime objects
        last = health["last_completed_at"]
        last_str = str(last) if not isinstance(last, str) else last
        assert "2026-04-01" in last_str and "12:00:00" in last_str

    def test_empty_queue_no_last_completed(self, empty_queue: Path):
        """Empty queue has None for last completed."""
        health = get_queue_health(empty_queue)
        assert health["last_completed_at"] is None


class TestScriptSafety:
    """Test shell script avoids embedded Python source interpolation."""

    def test_queue_health_avoids_python_c_fragments(self):
        script = QUEUE_HEALTH_SCRIPT.read_text()
        assert "python3 -c" not in script
        assert "uv run --no-project python -c" not in script

    def test_queue_health_uses_uv_run_for_python(self):
        script = QUEUE_HEALTH_SCRIPT.read_text()
        assert "uv run --no-project python -" in script

    def test_queue_health_reports_git_pull_failures(self):
        script = QUEUE_HEALTH_SCRIPT.read_text()
        assert "git_pull_failures" in script


class TestHealthReportFormat:
    """Test report formatting."""

    def test_report_contains_status(self, healthy_queue: Path):
        """Report string includes health status."""
        health = get_queue_health(healthy_queue)
        report = format_health_report(health)
        assert "HEALTHY" in report

    def test_report_contains_counts(self, unhealthy_queue: Path):
        """Report string includes all count lines."""
        health = get_queue_health(unhealthy_queue)
        report = format_health_report(health)
        assert "Pending jobs:" in report
        assert "Completed jobs:" in report
        assert "Failed jobs:" in report

    def test_report_header(self, empty_queue: Path):
        """Report starts with header line."""
        health = get_queue_health(empty_queue)
        report = format_health_report(health)
        assert report.startswith("=== Solver Queue Health ===")

    def test_report_na_when_no_completed(self, empty_queue: Path):
        """Last completed shows N/A when no jobs completed."""
        health = get_queue_health(empty_queue)
        report = format_health_report(health)
        assert "N/A" in report

    def test_report_shows_last_completed(self, healthy_queue: Path):
        """Report includes last completed timestamp."""
        health = get_queue_health(healthy_queue)
        report = format_health_report(health)
        assert "2026-04-01" in report and "12:00:00" in report


class TestCriticalStatus:
    """Test CRITICAL health status threshold."""

    def test_many_pending_plus_failures_is_critical(self, tmp_path: Path):
        """Queue with >5 pending AND failures = CRITICAL."""
        q = tmp_path / "queue"
        (q / "pending").mkdir(parents=True)
        (q / "completed").mkdir(parents=True)
        (q / "failed").mkdir(parents=True)

        # 6 pending
        for i in range(6):
            (q / "pending" / f"20260401T{10+i:02d}0000Z-job{i}.yaml").write_text(
                f"solver: orcawave\ninput_file: t{i}.owd\n"
            )
        # 1 failed
        fail = q / "failed" / "fail0"
        fail.mkdir()
        (fail / "result.yaml").write_text("status: failed\n")

        health = get_queue_health(q)
        assert health["health_status"] == "CRITICAL"
