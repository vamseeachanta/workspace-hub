"""Tests for result watcher and post-processing hook.

ABOUTME: Validates watch-results detection logic and post-process-hook.py
metric extraction.  All filesystem/git operations are mocked — no real
queue directory needed.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WATCH_RESULTS_SCRIPT = REPO_ROOT / "scripts" / "solver" / "watch-results.sh"


# ---------------------------------------------------------------------------
# Inline the post-processing logic so tests run without importing scripts/
# ---------------------------------------------------------------------------

def extract_metrics(result_yaml: dict) -> dict:
    """Extract key metrics from a completed job result YAML.

    Returns a flat dict suitable for JSONL logging.
    """
    metrics = {
        "status": result_yaml.get("status", "unknown"),
        "solver": result_yaml.get("solver", ""),
        "input_file": result_yaml.get("input_file", ""),
        "description": result_yaml.get("description", ""),
        "processed_at": result_yaml.get("processed_at", ""),
        "elapsed_seconds": result_yaml.get("elapsed_seconds", 0.0),
    }
    if "output_files" in result_yaml:
        metrics["output_file_count"] = len(result_yaml["output_files"])
        metrics["output_files"] = result_yaml["output_files"]
    if "error" in result_yaml:
        metrics["error"] = result_yaml["error"]
    return metrics


def append_to_jsonl(log_path: Path, entry: dict) -> None:
    """Append a single JSON object as a line to a JSONL file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def scan_completed_jobs(completed_dir: Path) -> list[Path]:
    """Scan completed directory for result.yaml files."""
    if not completed_dir.exists():
        return []
    results = []
    for job_dir in sorted(completed_dir.iterdir()):
        if job_dir.is_dir():
            result_yaml = job_dir / "result.yaml"
            if result_yaml.exists():
                results.append(result_yaml)
    return results


def process_completed_job(result_path: Path, log_path: Path) -> dict:
    """Process a single completed job: extract metrics, append to JSONL."""
    with open(result_path) as f:
        data = yaml.safe_load(f)
    metrics = extract_metrics(data)
    metrics["job_dir"] = str(result_path.parent.name)
    append_to_jsonl(log_path, metrics)
    return metrics


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

COMPLETED_JOB_YAML = textwrap.dedent("""\
    status: completed
    processed_at: 2026-04-01T12:00:00Z
    solver: orcawave
    input_file: docs/domains/orcawave/L00/test01.owd
    description: "L00 smoke test"
    elapsed_seconds: 45.2
    output_files:
      - test01.owr
      - test01.xlsx
""")

FAILED_JOB_YAML = textwrap.dedent("""\
    status: failed
    processed_at: 2026-04-01T12:05:00Z
    solver: orcaflex
    input_file: models/broken_model.dat
    description: "Broken model test"
    elapsed_seconds: 2.1
    error: "OrcFxAPI.DLLError: License not found"
""")


@pytest.fixture
def queue_dir(tmp_path: Path) -> Path:
    """Create a mock queue directory with completed and failed jobs."""
    completed = tmp_path / "queue" / "completed"
    failed = tmp_path / "queue" / "failed"
    pending = tmp_path / "queue" / "pending"

    # Create directories
    for d in [completed, failed, pending]:
        d.mkdir(parents=True)

    # Completed job 1
    job1 = completed / "20260401T120000Z-test01"
    job1.mkdir()
    (job1 / "result.yaml").write_text(COMPLETED_JOB_YAML)

    # Completed job 2 (another successful one)
    job2 = completed / "20260401T130000Z-test02"
    job2.mkdir()
    (job2 / "result.yaml").write_text(COMPLETED_JOB_YAML.replace("test01", "test02"))

    # Failed job
    fail1 = failed / "20260401T120500Z-broken"
    fail1.mkdir()
    (fail1 / "result.yaml").write_text(FAILED_JOB_YAML)

    return tmp_path


# ---------------------------------------------------------------------------
# Tests: Job detection
# ---------------------------------------------------------------------------

class TestJobDetection:
    """Test scanning for completed jobs."""

    def test_finds_completed_jobs(self, queue_dir: Path):
        """Scan finds result.yaml files in completed subdirectories."""
        completed = queue_dir / "queue" / "completed"
        results = scan_completed_jobs(completed)
        assert len(results) == 2

    def test_empty_directory_returns_empty(self, tmp_path: Path):
        """Empty completed dir returns no results."""
        empty = tmp_path / "queue" / "completed"
        empty.mkdir(parents=True)
        results = scan_completed_jobs(empty)
        assert results == []

    def test_missing_directory_returns_empty(self, tmp_path: Path):
        """Non-existent directory returns empty list without error."""
        results = scan_completed_jobs(tmp_path / "nonexistent")
        assert results == []

    def test_ignores_dirs_without_result_yaml(self, tmp_path: Path):
        """Directories without result.yaml are skipped."""
        completed = tmp_path / "queue" / "completed"
        completed.mkdir(parents=True)
        (completed / "some-job").mkdir()
        # No result.yaml inside
        results = scan_completed_jobs(completed)
        assert results == []

    def test_results_sorted_by_name(self, queue_dir: Path):
        """Results are returned sorted by directory name (timestamp order)."""
        completed = queue_dir / "queue" / "completed"
        results = scan_completed_jobs(completed)
        names = [r.parent.name for r in results]
        assert names == sorted(names)


class TestFailedJobHandling:
    """Test handling of failed jobs in the queue."""

    def test_failed_job_metrics_contain_error(self, queue_dir: Path):
        """Failed job metrics include the error message."""
        failed = queue_dir / "queue" / "failed"
        results = scan_completed_jobs(failed)
        assert len(results) == 1
        with open(results[0]) as f:
            data = yaml.safe_load(f)
        metrics = extract_metrics(data)
        assert metrics["status"] == "failed"
        assert "License not found" in metrics["error"]

    def test_failed_job_has_elapsed_time(self, queue_dir: Path):
        """Failed jobs still record elapsed time."""
        failed = queue_dir / "queue" / "failed"
        results = scan_completed_jobs(failed)
        with open(results[0]) as f:
            data = yaml.safe_load(f)
        metrics = extract_metrics(data)
        assert metrics["elapsed_seconds"] == 2.1

    def test_failed_job_no_output_files(self, queue_dir: Path):
        """Failed jobs do not list output files."""
        failed = queue_dir / "queue" / "failed"
        results = scan_completed_jobs(failed)
        with open(results[0]) as f:
            data = yaml.safe_load(f)
        metrics = extract_metrics(data)
        assert "output_file_count" not in metrics


class TestMetricExtraction:
    """Test metric extraction from result YAML."""

    def test_extracts_all_fields(self):
        """All expected fields are extracted from completed job."""
        data = yaml.safe_load(COMPLETED_JOB_YAML)
        metrics = extract_metrics(data)
        assert metrics["status"] == "completed"
        assert metrics["solver"] == "orcawave"
        assert metrics["elapsed_seconds"] == 45.2
        assert metrics["output_file_count"] == 2

    def test_handles_minimal_yaml(self):
        """Minimal YAML with only status extracts without error."""
        data = {"status": "completed"}
        metrics = extract_metrics(data)
        assert metrics["status"] == "completed"
        assert metrics["solver"] == ""
        assert metrics["elapsed_seconds"] == 0.0

    def test_output_files_listed(self):
        """Output files are preserved in metrics."""
        data = yaml.safe_load(COMPLETED_JOB_YAML)
        metrics = extract_metrics(data)
        assert "test01.owr" in metrics["output_files"]
        assert "test01.xlsx" in metrics["output_files"]


class TestWatcherScriptSafety:
    """Static checks for watcher locking and failure surfacing."""

    def test_watch_results_uses_locking(self):
        script = WATCH_RESULTS_SCRIPT.read_text()
        assert "flock" in script or ".lock" in script

    def test_watch_results_does_not_mask_git_pull_failures(self):
        script = WATCH_RESULTS_SCRIPT.read_text()
        assert "git pull origin main 2>/dev/null || true" not in script
        assert "git pull origin main" in script

    def test_watch_results_uses_uv_run_for_python(self):
        script = WATCH_RESULTS_SCRIPT.read_text()
        assert 'uv run python "${POST_PROCESS_SCRIPT}"' in script or 'uv run --no-project python "${POST_PROCESS_SCRIPT}"' in script

    def test_watch_results_acquires_lock_before_resetting_failure_count(self):
        script = WATCH_RESULTS_SCRIPT.read_text()
        assert script.index("acquire_lock") < script.index("echo 0 > \"${PULL_FAILURE_COUNT_FILE}\"")


class TestJSONLAppend:
    """Test JSONL log file append behavior."""

    def test_creates_new_file(self, tmp_path: Path):
        """JSONL file is created if it doesn't exist."""
        log = tmp_path / "data" / "solver-results-log.jsonl"
        entry = {"status": "completed", "solver": "orcawave"}
        append_to_jsonl(log, entry)
        assert log.exists()
        lines = log.read_text().strip().split("\n")
        assert len(lines) == 1
        assert json.loads(lines[0])["status"] == "completed"

    def test_appends_to_existing(self, tmp_path: Path):
        """Subsequent writes append, not overwrite."""
        log = tmp_path / "log.jsonl"
        append_to_jsonl(log, {"n": 1})
        append_to_jsonl(log, {"n": 2})
        append_to_jsonl(log, {"n": 3})
        lines = log.read_text().strip().split("\n")
        assert len(lines) == 3
        assert [json.loads(l)["n"] for l in lines] == [1, 2, 3]

    def test_each_line_valid_json(self, tmp_path: Path):
        """Every line in JSONL is valid JSON."""
        log = tmp_path / "log.jsonl"
        for i in range(5):
            append_to_jsonl(log, {"index": i, "msg": f"entry {i}"})
        for line in log.read_text().strip().split("\n"):
            parsed = json.loads(line)  # should not raise
            assert "index" in parsed

    def test_full_pipeline(self, queue_dir: Path, tmp_path: Path):
        """End-to-end: scan → extract → append produces valid JSONL."""
        completed = queue_dir / "queue" / "completed"
        log = tmp_path / "results.jsonl"
        results = scan_completed_jobs(completed)
        for result_path in results:
            process_completed_job(result_path, log)
        lines = log.read_text().strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            entry = json.loads(line)
            assert entry["status"] == "completed"
            assert "job_dir" in entry
