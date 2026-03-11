"""TDD tests for scripts/memory/compact-memory.py

All tests are written BEFORE implementation (RED phase).
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "memory" / "compact-memory.py"


def run_script(*args: str, memory_root: Path, work_queue_root: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable, str(SCRIPT),
        "--memory-root", str(memory_root),
    ]
    if work_queue_root:
        cmd += ["--work-queue-root", str(work_queue_root)]
    cmd += list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


# ── T1: dry-run writes no files ──────────────────────────────────────────────

def test_dry_run_writes_no_files(memory_root: Path, work_queue_root: Path) -> None:
    """--dry-run prints audit, writes nothing."""
    before = {p: p.read_text() for p in memory_root.rglob("*.md")}
    result = run_script("--dry-run", memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr
    after = {p: p.read_text() for p in memory_root.rglob("*.md")}
    assert before == after, "dry-run must not modify any files"
    # audit report contains key sections
    assert "audit" in result.stdout.lower() or "eviction" in result.stdout.lower()


# ── T2: done-WRK eviction ────────────────────────────────────────────────────

def test_done_wrk_eviction(memory_root: Path, work_queue_root: Path) -> None:
    """Bullets referencing done WRK items are moved to archive/done-wrk.md."""
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    archive_file = memory_root / "archive" / "done-wrk.md"
    assert archive_file.exists(), "archive/done-wrk.md must be created"
    content = archive_file.read_text()
    assert "WRK-001" in content, "done-WRK bullet must appear in archive"

    # original topic file should not still contain the WRK-001 ref
    topic = (memory_root / "ai-orchestration.md").read_text()
    assert "WRK-001" not in topic


# ── T3: path staleness (opt-in) ──────────────────────────────────────────────

def test_path_staleness_flagged(memory_root: Path, work_queue_root: Path) -> None:
    """/tmp/nonexistent-path-xyz/ is flagged to archive/stale-paths.md when --check-paths is set."""
    result = run_script("--check-paths", memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    stale_file = memory_root / "archive" / "stale-paths.md"
    assert stale_file.exists(), "archive/stale-paths.md must be created with --check-paths"
    assert "nonexistent-path-xyz" in stale_file.read_text()


def test_path_staleness_skipped_without_flag(memory_root: Path, work_queue_root: Path) -> None:
    """Without --check-paths, stale paths are NOT flagged (cross-machine safety)."""
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    stale_file = memory_root / "archive" / "stale-paths.md"
    assert not stale_file.exists(), "stale-paths.md must NOT be created without --check-paths"


# ── T4: keep marker exempts age eviction ────────────────────────────────────

def test_keep_marker_survives_eviction(memory_root: Path, work_queue_root: Path) -> None:
    """Bullets marked # keep are NOT evicted by age eviction."""
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    topic = (memory_root / "ai-orchestration.md").read_text()
    assert "Sonnet 4.5 = default" in topic, "# keep bullet must survive"


# ── T5: keep marker does NOT exempt done-WRK eviction ───────────────────────

def test_keep_does_not_exempt_done_wrk(memory_root: Path, tmp_path: Path) -> None:
    """# keep does not protect a done-WRK reference from eviction."""
    # add a keep-marked done-WRK bullet
    topic = memory_root / "ai-orchestration.md"
    topic.write_text(
        topic.read_text() + "- WRK-001 old fact # keep\n",
        encoding="utf-8",
    )
    wq = tmp_path / "wq2"
    (wq / "archive" / "2026-01").mkdir(parents=True)
    (wq / "archive" / "2026-01" / "WRK-001.md").write_text(
        "---\nid: WRK-001\nstatus: done\n---\n",
        encoding="utf-8",
    )

    result = run_script(memory_root=memory_root, work_queue_root=wq)
    assert result.returncode == 0, result.stderr

    topic_text = topic.read_text()
    assert "WRK-001 old fact" not in topic_text, "done-WRK eviction ignores # keep"


# ── T6: compaction frees lines from oversized topic file ────────────────────

def test_lines_freed_from_oversized_file(memory_root: Path, work_queue_root: Path) -> None:
    """engineering-modules.md (>140L) is compacted to ≤140 lines."""
    before = len((memory_root / "engineering-modules.md").read_text().splitlines())
    assert before > 140, "fixture must start over the limit"

    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    after = len((memory_root / "engineering-modules.md").read_text().splitlines())
    assert after <= 140, f"file should be compacted to ≤140 lines, got {after}"
    assert before - after >= 10, "must free at least 10 lines"


# ── T7: idempotency ──────────────────────────────────────────────────────────

def test_idempotency(memory_root: Path, work_queue_root: Path) -> None:
    """Second run on already-compacted files produces zero evictions (topic files only)."""
    _GENERATED = {"compact-audit.md"}

    run_script(memory_root=memory_root, work_queue_root=work_queue_root)

    # compare only topic + MEMORY.md (not generated audit files)
    state_after_first = {
        p: p.read_text()
        for p in memory_root.rglob("*.md")
        if p.name not in _GENERATED
    }

    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    state_after_second = {
        p: p.read_text()
        for p in memory_root.rglob("*.md")
        if p.name not in _GENERATED
    }
    assert state_after_first == state_after_second, "second run must be a no-op on topic files"


# ── T8: compact-log.jsonl written ───────────────────────────────────────────

def test_compact_log_written(memory_root: Path, work_queue_root: Path) -> None:
    """compact-log.jsonl is appended with required fields."""
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    log_file = memory_root / "compact-log.jsonl"
    assert log_file.exists(), "compact-log.jsonl must be created"

    entry = json.loads(log_file.read_text().splitlines()[-1])
    for field in ("timestamp", "lines_freed_memory", "lines_freed_topics", "bullets_evicted", "bullets_archived", "trigger"):
        assert field in entry, f"compact-log.jsonl missing field: {field}"


# ── T9: zero-change run writes zero-change log entry ────────────────────────

def test_zero_change_idempotency_log(memory_root: Path, work_queue_root: Path) -> None:
    """Zero-change apply still writes a log entry (not silence)."""
    # first run to compact
    run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    log_before = (memory_root / "compact-log.jsonl").read_text().splitlines()

    # second run — should be a no-op but still log
    run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    log_after = (memory_root / "compact-log.jsonl").read_text().splitlines()

    assert len(log_after) == len(log_before) + 1, "zero-change run must append exactly one log entry"
    entry = json.loads(log_after[-1])
    assert entry["bullets_evicted"] == 0
    assert entry["bullets_archived"] == 0


# ── T10: ambiguous memory root fails fast ────────────────────────────────────

def test_missing_memory_root_fails(tmp_path: Path) -> None:
    """--memory-root pointing to nonexistent path exits non-zero with clear error."""
    result = run_script(
        "--dry-run",
        memory_root=tmp_path / "nonexistent",
        work_queue_root=tmp_path,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower()


# ── T11: malformed date degrades gracefully ──────────────────────────────────

def test_malformed_date_no_crash(memory_root: Path, work_queue_root: Path) -> None:
    """Bullet with malformed date marker does not crash — degrades to manual-review."""
    # inject a bullet with a bad date
    topic = memory_root / "ai-orchestration.md"
    topic.write_text(
        topic.read_text() + "- Old fact from NOT-A-DATE about something\n",
        encoding="utf-8",
    )
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, f"malformed date must not crash: {result.stderr}"


# ── T12: atomic write — file is valid after run ──────────────────────────────

def test_atomic_write_files_valid(memory_root: Path, work_queue_root: Path) -> None:
    """After compaction all .md files are non-empty and decodable UTF-8."""
    result = run_script(memory_root=memory_root, work_queue_root=work_queue_root)
    assert result.returncode == 0, result.stderr

    for md_file in memory_root.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        assert content, f"{md_file} must not be empty after compaction"
