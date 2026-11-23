"""TDD tests for WRK-1143: centralized wrk-status-index.json via shell scripts."""

import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).parents[2]
UPDATE_SCRIPT = WORKSPACE_ROOT / "scripts/work-queue/update-wrk-index.sh"
REBUILD_SCRIPT = WORKSPACE_ROOT / "scripts/work-queue/rebuild-wrk-index.sh"


def _make_queue(tmp_path: Path) -> Path:
    """Scaffold a minimal fake work-queue directory."""
    queue = tmp_path / "work-queue"
    for d in ("pending", "working", "blocked", "done", "archive"):
        (queue / d).mkdir(parents=True)
    (queue / "wrk-status-index.json").write_text("{}")
    return queue


def _make_wrk(queue: Path, loc: str, wrk_id: str, status: str = "pending",
              title: str = "Test WRK", priority: str = "medium",
              category: str = "test") -> Path:
    """Write a minimal frontmatter WRK file into queue/<loc>/."""
    f = queue / loc / f"{wrk_id}.md"
    f.write_text(textwrap.dedent(f"""\
        ---
        title: {title}
        status: {status}
        priority: {priority}
        category: {category}
        ---
        Body.
    """))
    return f


def _run_update(queue: Path, wrk_id: str, status: str, caller: str = "test") -> subprocess.CompletedProcess:
    env = {**os.environ, "WORK_QUEUE_ROOT": str(queue)}
    return subprocess.run(
        ["bash", str(UPDATE_SCRIPT), wrk_id, status, caller],
        capture_output=True, text=True, env=env,
    )


def _run_rebuild(queue: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "WORK_QUEUE_ROOT": str(queue)}
    return subprocess.run(
        ["bash", str(REBUILD_SCRIPT)],
        capture_output=True, text=True, env=env,
    )


def _read_index(queue: Path) -> dict:
    return json.loads((queue / "wrk-status-index.json").read_text())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_update_creates_entry(tmp_path):
    queue = _make_queue(tmp_path)
    _make_wrk(queue, "pending", "WRK-9001")
    result = _run_update(queue, "WRK-9001", "pending")
    assert result.returncode == 0, result.stderr
    data = _read_index(queue)
    assert "WRK-9001" in data
    assert data["WRK-9001"]["status"] == "pending"


def test_update_upserts_idempotent(tmp_path):
    queue = _make_queue(tmp_path)
    _make_wrk(queue, "pending", "WRK-9002")
    _run_update(queue, "WRK-9002", "pending", "first")
    _run_update(queue, "WRK-9002", "pending", "second")
    data = _read_index(queue)
    assert list(data.keys()).count("WRK-9002") == 1, "duplicate keys in JSON"
    assert data["WRK-9002"]["status"] == "pending"


def test_update_fields_populated(tmp_path):
    queue = _make_queue(tmp_path)
    _make_wrk(queue, "working", "WRK-9003", status="working",
               title="My Title", priority="high", category="ai")
    result = _run_update(queue, "WRK-9003", "working", "claim-item")
    assert result.returncode == 0, result.stderr
    entry = _read_index(queue)["WRK-9003"]
    assert entry["machine"] != ""
    assert entry["priority"] == "high"
    assert entry["category"] == "ai"
    assert entry["updated_by"] == "claim-item"
    assert "last_updated" in entry


def test_update_status_overwrite(tmp_path):
    queue = _make_queue(tmp_path)
    _make_wrk(queue, "pending", "WRK-9004")
    _run_update(queue, "WRK-9004", "pending")
    # move file to working dir and update with new status
    (queue / "pending" / "WRK-9004.md").rename(queue / "working" / "WRK-9004.md")
    _run_update(queue, "WRK-9004", "working")
    entry = _read_index(queue)["WRK-9004"]
    assert entry["status"] == "working"


def test_rebuild_produces_valid_json(tmp_path):
    queue = _make_queue(tmp_path)
    _make_wrk(queue, "pending", "WRK-9010")
    _make_wrk(queue, "working", "WRK-9011", status="working")
    result = _run_rebuild(queue)
    assert result.returncode == 0, result.stderr
    data = _read_index(queue)
    assert isinstance(data, dict)
    assert "WRK-9010" in data
    assert "WRK-9011" in data


def test_rebuild_clears_stale_entries(tmp_path):
    queue = _make_queue(tmp_path)
    # Seed the index with a stale entry
    (queue / "wrk-status-index.json").write_text(
        json.dumps({"WRK-STALE": {"status": "pending", "machine": "old"}})
    )
    _make_wrk(queue, "pending", "WRK-9020")
    result = _run_rebuild(queue)
    assert result.returncode == 0, result.stderr
    data = _read_index(queue)
    assert "WRK-STALE" not in data, "stale entry not cleared by rebuild"
    assert "WRK-9020" in data
