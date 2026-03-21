"""
Tests T60–T68: Centralized WRK Status Index (WRK-1143, WRK-5105).

T60: rebuild-wrk-index.sh on temp queue dir → valid JSON with correct status values
T61: update-wrk-index.sh upserts new entry; repeat call overwrites cleanly (no duplicates)
T62: update-wrk-index.sh creates index file when none exists
T63: update-wrk-index.sh with missing WRK-ID exits 1 with stderr message
T64: claim-item.sh source contains "update-wrk-index" (wiring gate)
T65: whats-next.sh source contains "--debug" flag handling (wiring gate)
T66: update-wrk-index.sh extracts enriched fields (subcategory, created_at, etc.)
T67: rebuild-wrk-index.sh computes urgency_score for non-archived entries
T68: whats-next.sh source uses index-first data path (no uv run urgency_score.py)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_wrk(
    path: Path,
    wrk_id: str,
    status: str,
    title: str = "Test",
    priority: str = "medium",
    category: str = "harness",
) -> None:
    """Write a minimal WRK .md file with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nid: {wrk_id}\ntitle: {title}\nstatus: {status}\npriority: {priority}\ncategory: {category}\n---\n\nBody.\n"
    )


def _run_script(script_name: str, args: list[str], env_overrides: dict | None = None) -> subprocess.CompletedProcess:
    """Run a bash script from SCRIPTS_DIR with optional env overrides."""
    script_path = SCRIPTS_DIR / script_name
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(script_path)] + args,
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# T60: rebuild-wrk-index.sh on temp queue dir → valid JSON with correct statuses
# ---------------------------------------------------------------------------

class TestT60RebuildIndex:
    def test_rebuild_produces_valid_json_with_correct_statuses(self, tmp_path):
        """T60: rebuild-wrk-index.sh on temp dir → valid JSON, WRK-9001=pending, WRK-9002=working."""
        # Arrange: create temp queue structure
        _write_wrk(
            tmp_path / "pending" / "WRK-9001.md",
            wrk_id="WRK-9001",
            title="Test Item",
            status="pending",
            priority="medium",
            category="harness",
        )
        _write_wrk(
            tmp_path / "working" / "WRK-9002.md",
            wrk_id="WRK-9002",
            title="Working Item",
            status="working",
            priority="high",
            category="harness",
        )

        # Act: run rebuild with WORK_QUEUE_ROOT pointing at tmp_path
        result = _run_script(
            "rebuild-wrk-index.sh",
            [],
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )

        # Assert: script exited cleanly
        assert result.returncode == 0, f"rebuild-wrk-index.sh failed:\nstdout={result.stdout}\nstderr={result.stderr}"

        # Assert: index file created
        index_path = tmp_path / "wrk-status-index.json"
        assert index_path.exists(), "wrk-status-index.json was not created"

        # Assert: valid JSON
        index = json.loads(index_path.read_text())

        # Assert: correct status values
        assert "WRK-9001" in index, f"WRK-9001 not found in index: {list(index.keys())}"
        assert "WRK-9002" in index, f"WRK-9002 not found in index: {list(index.keys())}"
        assert index["WRK-9001"]["status"] == "pending"
        assert index["WRK-9002"]["status"] == "working"


# ---------------------------------------------------------------------------
# T61: update-wrk-index.sh upserts; repeat call overwrites cleanly
# ---------------------------------------------------------------------------

class TestT61UpsertOverwrite:
    def test_upsert_overwrites_existing_entry_without_duplication(self, tmp_path):
        """T61: update-wrk-index.sh called twice → same key, status updated, not duplicated."""
        # Arrange: a pending WRK file
        _write_wrk(
            tmp_path / "pending" / "WRK-9010.md",
            wrk_id="WRK-9010",
            status="pending",
        )

        env = {"WORK_QUEUE_ROOT": str(tmp_path)}

        # Act: first call → working
        result1 = _run_script("update-wrk-index.sh", ["WRK-9010", "working"], env_overrides=env)
        assert result1.returncode == 0, f"First call failed:\nstdout={result1.stdout}\nstderr={result1.stderr}"

        index_path = tmp_path / "wrk-status-index.json"
        assert index_path.exists()
        index_after_first = json.loads(index_path.read_text())
        assert index_after_first["WRK-9010"]["status"] == "working"

        # Act: second call → done
        result2 = _run_script("update-wrk-index.sh", ["WRK-9010", "done"], env_overrides=env)
        assert result2.returncode == 0, f"Second call failed:\nstdout={result2.stdout}\nstderr={result2.stderr}"

        # Assert: only one key, status is now "done"
        index_after_second = json.loads(index_path.read_text())
        assert index_after_second["WRK-9010"]["status"] == "done"
        # Verify no duplication — JSON object keys are unique by definition, so
        # count by re-parsing and checking key count didn't balloon
        raw_text = index_path.read_text()
        assert raw_text.count('"WRK-9010"') == 1, "WRK-9010 key appears more than once (duplication bug)"


# ---------------------------------------------------------------------------
# T62: update-wrk-index.sh creates index file when none exists
# ---------------------------------------------------------------------------

class TestT62CreatesIndexIfAbsent:
    def test_creates_index_file_when_not_present(self, tmp_path):
        """T62: update-wrk-index.sh with no pre-existing index → file created, valid JSON."""
        # Arrange: WRK file, no index file
        _write_wrk(
            tmp_path / "pending" / "WRK-9020.md",
            wrk_id="WRK-9020",
            status="pending",
        )
        index_path = tmp_path / "wrk-status-index.json"
        assert not index_path.exists(), "Pre-condition failed: index should not exist yet"

        # Act
        result = _run_script(
            "update-wrk-index.sh",
            ["WRK-9020", "pending"],
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )

        # Assert: script succeeded and created a valid JSON file
        assert result.returncode == 0, f"Script failed:\nstdout={result.stdout}\nstderr={result.stderr}"
        assert index_path.exists(), "Index file was not created"
        index = json.loads(index_path.read_text())
        assert "WRK-9020" in index
        assert index["WRK-9020"]["status"] == "pending"


# ---------------------------------------------------------------------------
# T63: update-wrk-index.sh with missing WRK-ID exits 1 with stderr message
# ---------------------------------------------------------------------------

class TestT63MissingArgExitsOne:
    def test_no_wrk_id_arg_exits_1_with_stderr(self, tmp_path):
        """T63: update-wrk-index.sh called with no arguments → exit 1, stderr non-empty."""
        result = _run_script(
            "update-wrk-index.sh",
            [],  # no arguments
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )

        assert result.returncode == 1, (
            f"Expected exit code 1, got {result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        assert result.stderr.strip(), (
            f"Expected non-empty stderr, got empty string\nstdout={result.stdout}"
        )

    def test_nonexistent_wrk_id_proceeds_gracefully(self, tmp_path):
        """T63b: update-wrk-index.sh with a WRK-ID not in any queue dir → exits 0, writes entry.

        The plan spec says exit 1 only on *missing argument*. When the WRK file is simply
        absent (e.g., already archived or deleted), the script should still write the entry
        with empty title/priority/category so status updates are never lost.
        """
        result = _run_script(
            "update-wrk-index.sh",
            ["WRK-0000", "working"],  # WRK-0000 doesn't exist in tmp_path
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )

        assert result.returncode == 0, (
            f"Expected exit code 0 (graceful), got {result.returncode}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
        idx_path = tmp_path / "wrk-status-index.json"
        assert idx_path.exists(), "Index file should have been created"
        data = json.loads(idx_path.read_text())
        assert data.get("WRK-0000", {}).get("status") == "working"


# ---------------------------------------------------------------------------
# T64: claim-item.sh source contains "update-wrk-index" (wiring gate)
# ---------------------------------------------------------------------------

class TestT64ClaimItemWired:
    def test_claim_item_source_references_update_wrk_index(self):
        """T64: claim-item.sh script source contains 'update-wrk-index' (wiring gate)."""
        claim_script = SCRIPTS_DIR / "claim-item.sh"
        assert claim_script.exists(), f"claim-item.sh not found at {claim_script}"

        content = claim_script.read_text()
        assert "update-wrk-index" in content, (
            "claim-item.sh does not reference 'update-wrk-index' — "
            "wiring to the index not yet implemented"
        )


# ---------------------------------------------------------------------------
# T65: whats-next.sh source contains "--debug" and index-read wiring
# ---------------------------------------------------------------------------

class TestT65WhatsNextDebugWired:
    def test_whats_next_source_contains_debug_flag(self):
        """T65: whats-next.sh source contains '--debug' flag handling (wiring gate)."""
        script = SCRIPTS_DIR / "whats-next.sh"
        assert script.exists(), f"whats-next.sh not found at {script}"

        content = script.read_text()
        assert "--debug" in content, (
            "whats-next.sh does not handle '--debug' flag — "
            "debug/index annotation wiring not yet implemented"
        )

    def test_whats_next_source_references_index(self):
        """T65b: whats-next.sh source references 'wrk-status-index' or 'read_index_status'."""
        script = SCRIPTS_DIR / "whats-next.sh"
        assert script.exists(), f"whats-next.sh not found at {script}"

        content = script.read_text()
        wired = "wrk-status-index" in content or "read_index_status" in content
        assert wired, (
            "whats-next.sh does not reference 'wrk-status-index' or 'read_index_status' — "
            "index read wiring not yet implemented"
        )


# ---------------------------------------------------------------------------
# T66: update-wrk-index.sh extracts enriched fields (subcategory, etc.)
# ---------------------------------------------------------------------------

def _write_enriched_wrk(path: Path, wrk_id: str) -> None:
    """Write a WRK file with all enriched frontmatter fields."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\n"
        f"id: {wrk_id}\n"
        f"title: Enriched Test Item\n"
        f"status: pending\n"
        f"priority: high\n"
        f"category: engineering\n"
        f"subcategory: structural\n"
        f"created_at: 2026-03-01\n"
        f"blocked_by: []\n"
        f'github_issue_ref: https://github.com/test/repo/issues/42\n'
        f"type: task\n"
        f"computer: dev-primary\n"
        f"---\n\nBody.\n"
    )


class TestT66EnrichedFields:
    def test_update_extracts_enriched_fields(self, tmp_path):
        """T66: update-wrk-index.sh extracts subcategory, created_at, github_issue_ref, etc."""
        _write_enriched_wrk(tmp_path / "pending" / "WRK-9030.md", "WRK-9030")

        result = _run_script(
            "update-wrk-index.sh",
            ["WRK-9030", "pending"],
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"

        index = json.loads((tmp_path / "wrk-status-index.json").read_text())
        entry = index["WRK-9030"]

        assert entry["subcategory"] == "structural"
        assert entry["created_at"] == "2026-03-01"
        assert "github.com" in entry["github_issue_ref"]
        assert entry["type"] == "task"
        assert entry["computer"] == "dev-primary"
        assert entry["category"] == "engineering"


# ---------------------------------------------------------------------------
# T67: rebuild-wrk-index.sh computes urgency_score for non-archived entries
# ---------------------------------------------------------------------------

class TestT67UrgencyScoreComputed:
    def test_rebuild_computes_urgency_scores(self, tmp_path):
        """T67: rebuild-wrk-index.sh post-pass writes urgency_score for pending items."""
        _write_enriched_wrk(tmp_path / "pending" / "WRK-9040.md", "WRK-9040")

        result = _run_script(
            "rebuild-wrk-index.sh",
            [],
            env_overrides={"WORK_QUEUE_ROOT": str(tmp_path)},
        )
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"

        index = json.loads((tmp_path / "wrk-status-index.json").read_text())
        entry = index["WRK-9040"]

        assert "urgency_score" in entry, "urgency_score not computed by rebuild"
        assert isinstance(entry["urgency_score"], (int, float))
        assert entry["urgency_score"] > 0, "urgency_score should be positive for high-priority item"


# ---------------------------------------------------------------------------
# T68: whats-next.sh uses index-first path (no uv run urgency_score.py)
# ---------------------------------------------------------------------------

class TestT68IndexFirstPath:
    def test_whats_next_does_not_call_urgency_score_py(self):
        """T68: whats-next.sh should not call uv run urgency_score.py at runtime."""
        script = SCRIPTS_DIR / "whats-next.sh"
        content = script.read_text()
        assert "urgency_score.py" not in content, (
            "whats-next.sh still references urgency_score.py — "
            "should use pre-computed scores from index"
        )

    def test_whats_next_has_compact_flag(self):
        """T68b: whats-next.sh supports --compact flag."""
        script = SCRIPTS_DIR / "whats-next.sh"
        content = script.read_text()
        assert "--compact" in content, "whats-next.sh missing --compact flag support"
