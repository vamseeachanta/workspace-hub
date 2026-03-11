"""TDD tests for scripts/memory/eval-memory-quality.py

All tests written BEFORE implementation (RED phase).
Read-only: eval script must never modify memory files.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "memory" / "eval-memory-quality.py"


def run_eval(*args: str, memory_root: Path) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--memory-root", str(memory_root), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.fixture()
def mem_root(tmp_path: Path) -> Path:
    """Minimal memory root with known content for deterministic metric checks."""
    root = tmp_path / "memory"
    root.mkdir()

    # MEMORY.md: 10 lines total, 3 bullet lines
    (root / "MEMORY.md").write_text(
        "# Memory\n\n"
        "## Section\n"
        "- WRK-001 done item ref\n"
        "- WRK-002 active item\n"
        "- plain bullet\n"
        "\n"
        "## Another\n"
        "- more content\n"
        "- last bullet\n",
        encoding="utf-8",
    )

    # topic file: 8 lines total, 2 bullet lines
    topic = root / "engineering.md"
    topic.write_text(
        "# Engineering\n\n"
        "## Work\n"
        "- WRK-003 archived item ref\n"
        "- normal fact here\n"
        "\n"
        "## More\n"
        "- extra\n",
        encoding="utf-8",
    )

    # work-queue archive stub so WRK-001 and WRK-003 resolve as done
    wq = tmp_path / "work-queue"
    archive = wq / "archive" / "2026-01"
    archive.mkdir(parents=True)
    (archive / "WRK-001.md").write_text("---\nid: WRK-001\nstatus: done\n---\n", encoding="utf-8")
    (archive / "WRK-003.md").write_text("---\nid: WRK-003\nstatus: done\n---\n", encoding="utf-8")

    return root


# ── T1: exits 0 and emits JSON with all 6 metrics ────────────────────────────

def test_exits_zero_and_json_has_all_metrics(mem_root: Path) -> None:
    """--memory-root exits 0 and JSON output contains all 6 required metrics."""
    result = run_eval(memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    for key in (
        "pct_done_wrk",
        "pct_stale_paths",
        "signal_density",
        "memory_md_headroom",
        "topic_file_headroom",
        "dedup_candidates",
    ):
        assert key in data, f"metric '{key}' missing from JSON output"


# ── T2: pct_done_wrk metric ──────────────────────────────────────────────────

def test_pct_done_wrk_metric(mem_root: Path, tmp_path: Path) -> None:
    """pct_done_wrk counts bullets referencing done WRK items.

    Fixture: 7 bullet lines total, 2 reference done WRKs (WRK-001, WRK-003).
    Expected: 2/7 ≈ 28.57%
    """
    wq = tmp_path / "work-queue"
    result = run_eval("--work-queue-root", str(wq), memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    # 2 done-WRK bullets out of 7 total bullets → ~28.57
    assert 25.0 <= data["pct_done_wrk"] <= 35.0, (
        f"pct_done_wrk={data['pct_done_wrk']}, expected ~28.57"
    )


# ── T3: signal_density metric ────────────────────────────────────────────────

def test_signal_density_metric(mem_root: Path) -> None:
    """signal_density = total bullets / total lines across MEMORY.md + topic files."""
    result = run_eval(memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    # 7 bullets / 18 lines = 0.388...
    sd = data["signal_density"]
    assert 0.30 <= sd <= 0.50, f"signal_density={sd}, expected ~0.388"


# ── T4: memory_md_headroom metric ────────────────────────────────────────────

def test_memory_md_headroom(mem_root: Path) -> None:
    """memory_md_headroom = 180 - len(MEMORY.md lines)."""
    result = run_eval(memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    # MEMORY.md has 10 lines → headroom = 180 - 10 = 170
    assert data["memory_md_headroom"] == 170, (
        f"memory_md_headroom={data['memory_md_headroom']}, expected 170"
    )


# ── T5: topic_file_headroom metric ───────────────────────────────────────────

def test_topic_file_headroom(mem_root: Path) -> None:
    """topic_file_headroom is a dict mapping filename → lines remaining before 140L."""
    result = run_eval(memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    tfh = data["topic_file_headroom"]
    assert isinstance(tfh, dict), "topic_file_headroom must be a dict"
    assert "engineering.md" in tfh, "topic file must appear in headroom dict"
    # engineering.md has 8 lines → headroom = 140 - 8 = 132
    assert tfh["engineering.md"] == 132, (
        f"engineering.md headroom={tfh['engineering.md']}, expected 132"
    )


# ── T6: dedup_candidates metric ──────────────────────────────────────────────

def test_dedup_candidates_metric(tmp_path: Path) -> None:
    """dedup_candidates counts bullets with >=90% token overlap."""
    root = tmp_path / "dedup_mem"
    root.mkdir()
    (root / "MEMORY.md").write_text("# Memory\n", encoding="utf-8")
    # two near-identical bullets → 1 dedup candidate
    topic = root / "dupes.md"
    topic.write_text(
        "# Topic\n"
        "- The quick brown fox jumped over the lazy dog near the fence\n"
        "- The quick brown fox jumped over the lazy dog near the fence today\n"
        "- completely different line about something else\n",
        encoding="utf-8",
    )
    result = run_eval(memory_root=root)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["dedup_candidates"] >= 1, (
        f"dedup_candidates={data['dedup_candidates']}, expected >=1"
    )


# ── T7: --format md emits markdown table ─────────────────────────────────────

def test_format_md_flag(mem_root: Path) -> None:
    """--format md produces a markdown table (contains | characters and metric names)."""
    result = run_eval("--format", "md", memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    output = result.stdout
    assert "|" in output, "markdown output must contain table pipe characters"
    assert "pct_done_wrk" in output or "done_wrk" in output, (
        "markdown table must reference pct_done_wrk metric"
    )
    assert "signal_density" in output, "markdown table must reference signal_density"


# ── T8: --compare mode shows delta ───────────────────────────────────────────

def test_compare_mode(tmp_path: Path) -> None:
    """--compare before.json after.json prints delta per metric."""
    before = {
        "pct_done_wrk": 10.0,
        "pct_stale_paths": 5.0,
        "signal_density": 0.3,
        "memory_md_headroom": 150,
        "topic_file_headroom": {"a.md": 100},
        "dedup_candidates": 3,
    }
    after = {
        "pct_done_wrk": 5.0,
        "pct_stale_paths": 2.0,
        "signal_density": 0.35,
        "memory_md_headroom": 155,
        "topic_file_headroom": {"a.md": 110},
        "dedup_candidates": 1,
    }
    before_file = tmp_path / "before.json"
    after_file = tmp_path / "after.json"
    before_file.write_text(json.dumps(before), encoding="utf-8")
    after_file.write_text(json.dumps(after), encoding="utf-8")

    cmd = [
        sys.executable, str(SCRIPT),
        "--compare", str(before_file), str(after_file),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    output = result.stdout
    # delta for pct_done_wrk = -5.0
    assert "pct_done_wrk" in output, "compare output must reference pct_done_wrk"
    assert "-5" in output or "−5" in output or "-5.0" in output, (
        "compare output must show negative delta for pct_done_wrk"
    )


# ── T9: read-only — no files modified ────────────────────────────────────────

def test_read_only_no_files_modified(mem_root: Path) -> None:
    """eval script must not write or modify any files in memory root."""
    before = {p: p.read_bytes() for p in mem_root.rglob("*") if p.is_file()}
    result = run_eval(memory_root=mem_root)
    assert result.returncode == 0, result.stderr
    after = {p: p.read_bytes() for p in mem_root.rglob("*") if p.is_file()}
    assert before == after, "eval script must not modify any files (read-only)"


# ── T10: missing memory root fails with clear error ──────────────────────────

def test_missing_memory_root_fails(tmp_path: Path) -> None:
    """--memory-root pointing to nonexistent path exits non-zero with clear message."""
    result = run_eval(memory_root=tmp_path / "nonexistent")
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower()
