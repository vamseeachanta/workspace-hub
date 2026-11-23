"""TDD tests for scripts/memory/curate-memory.py

All tests are written BEFORE implementation (RED phase).
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "memory" / "curate-memory.py"


def run_script(*args: str, memory_root: Path, candidates_dir: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable, str(SCRIPT),
        "--memory-root", str(memory_root),
    ]
    if candidates_dir:
        cmd += ["--candidates-dir", str(candidates_dir)]
    cmd += list(args)
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.fixture()
def curate_memory_root(tmp_path: Path) -> Path:
    root = tmp_path / "memory"
    root.mkdir()
    (root / "MEMORY.md").write_text(
        textwrap.dedent("""\
        # Workspace Hub Memory

        ## Environment
        - **Python runtime**: `uv run` for ALL repos
        - **assethold** test counts: 990 pass
        """),
        encoding="utf-8",
    )
    (root / "ai-orchestration.md").write_text(
        textwrap.dedent("""\
        # AI Orchestration

        ## Tools
        - Sonnet 4.5 = default; use for all standard tasks
        - Run `uv run --no-project python -m pytest tests/` for hub scripts
        - NEVER reference 0113 or Orc DR in ported code (legal requirement)
        - The digitalmodel benchmark_plotter.py is over 2700 lines — refactor candidate
        """),
        encoding="utf-8",
    )
    return root


# ── T1: runs cleanly and exits 0 ─────────────────────────────────────────────

def test_curate_runs_cleanly(curate_memory_root: Path, tmp_path: Path) -> None:
    result = run_script(memory_root=curate_memory_root, candidates_dir=tmp_path / "candidates")
    assert result.returncode == 0, result.stderr


# ── T2: promotion candidates file written ────────────────────────────────────

def test_promotion_candidates_written(curate_memory_root: Path, tmp_path: Path) -> None:
    candidates_dir = tmp_path / "candidates"
    result = run_script(memory_root=curate_memory_root, candidates_dir=candidates_dir)
    assert result.returncode == 0, result.stderr

    cand_file = candidates_dir / "memory-promotion-candidates.md"
    assert cand_file.exists(), "memory-promotion-candidates.md must be created"
    content = cand_file.read_text()
    assert len(content.strip()) > 0, "candidates file must not be empty"


# ── T3: legal rule classified as memory-keep ─────────────────────────────────

def test_legal_rule_classified_memory_keep(curate_memory_root: Path, tmp_path: Path) -> None:
    """'NEVER reference 0113' is a foundational invariant — classified memory-keep → not in candidates."""
    candidates_dir = tmp_path / "candidates"
    run_script(memory_root=curate_memory_root, candidates_dir=candidates_dir)
    content = (candidates_dir / "memory-promotion-candidates.md").read_text()
    # memory-keep bullets are NOT written to candidates file
    assert "0113" not in content, "legal 'NEVER reference' rule must be memory-keep (absent from candidates)"


# ── T4: refactor candidate classified as skill-update or domain-doc ──────────

def test_refactor_candidate_classified(curate_memory_root: Path, tmp_path: Path) -> None:
    """'benchmark_plotter.py over 2700 lines' should not stay in raw memory."""
    candidates_dir = tmp_path / "candidates"
    run_script(memory_root=curate_memory_root, candidates_dir=candidates_dir)
    content = (candidates_dir / "memory-promotion-candidates.md").read_text()
    assert "benchmark_plotter" in content or "2700" in content


# ── T5: does not modify memory files ─────────────────────────────────────────

def test_curate_does_not_modify_memory(curate_memory_root: Path, tmp_path: Path) -> None:
    """curate-memory.py generates candidates only — never writes back to memory files."""
    before = {p: p.read_text() for p in curate_memory_root.rglob("*.md")}
    run_script(memory_root=curate_memory_root, candidates_dir=tmp_path / "candidates")
    after = {p: p.read_text() for p in curate_memory_root.rglob("*.md")}
    assert before == after, "curate must not modify memory files"


# ── T6: keep-marked bullet classified memory-keep ───────────────────────────

def test_keep_marker_classified_memory_keep(curate_memory_root: Path, tmp_path: Path) -> None:
    """A bullet with '# keep' is classified memory-keep and absent from candidates."""
    (curate_memory_root / "extra.md").write_text(
        "# Extra\n- This is important context # keep\n",
        encoding="utf-8",
    )
    candidates_dir = tmp_path / "candidates"
    run_script(memory_root=curate_memory_root, candidates_dir=candidates_dir)
    content = (candidates_dir / "memory-promotion-candidates.md").read_text()
    assert "This is important context" not in content, "# keep bullet must not appear in candidates"


# ── T7: done-WRK bullet classified archive ──────────────────────────────────

def test_done_wrk_classified_archive(curate_memory_root: Path, tmp_path: Path) -> None:
    """Bullet referencing a done/archived WRK is classified archive."""
    (curate_memory_root / "extra.md").write_text(
        "# Extra\n- WRK-001 archived — legacy work complete\n",
        encoding="utf-8",
    )
    candidates_dir = tmp_path / "candidates"
    run_script(memory_root=curate_memory_root, candidates_dir=candidates_dir)
    content = (candidates_dir / "memory-promotion-candidates.md").read_text()
    assert "archive" in content.lower(), "done-WRK bullet should be classified archive"
    assert "WRK-001" in content


# ── T8: missing memory root exits non-zero ──────────────────────────────────

def test_missing_memory_root_fails(tmp_path: Path) -> None:
    """curate-memory.py exits non-zero with clear error for missing memory root."""
    result = run_script(
        memory_root=tmp_path / "nonexistent",
        candidates_dir=tmp_path / "out",
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower()
