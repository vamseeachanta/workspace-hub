"""Fixtures for memory compaction tests."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def memory_root(tmp_path: Path) -> Path:
    """Isolated memory root with realistic topic files and MEMORY.md."""
    root = tmp_path / "memory"
    root.mkdir()
    (root / "archive").mkdir()

    # MEMORY.md — 5 lines, within limit
    (root / "MEMORY.md").write_text(
        textwrap.dedent("""\
        # Workspace Hub Memory

        > Details: `engineering-modules.md`, `ai-orchestration.md`

        ## Environment
        - **Python runtime**: `uv run` for ALL repos
        - **assethold** test counts: 990 pass
        """),
        encoding="utf-8",
    )

    # topic file — 12 lines including a stale path, a done-WRK ref, a keep marker
    (root / "ai-orchestration.md").write_text(
        textwrap.dedent("""\
        # AI Orchestration

        ## Tools
        - **Sonnet 4.5 = default** # keep
        - Codex cross-review = HARD GATE
        - WRK-001 archived — old routing rule
        - File at /tmp/nonexistent-path-xyz/file.txt is important
        - Normal fact about something stable
        - Another stable fact
        - Yet another stable fact
        - Final stable fact
        """),
        encoding="utf-8",
    )

    # Oversized topic file (>150 lines) to trigger compaction and free >=10 lines
    lines = ["# Engineering Modules\n\n"]
    for i in range(155):
        lines.append(f"- Fact number {i}: some engineering detail\n")
    (root / "engineering-modules.md").write_text("".join(lines), encoding="utf-8")

    return root


@pytest.fixture()
def work_queue_root(tmp_path: Path) -> Path:
    """Minimal work-queue structure with one done WRK item."""
    wq = tmp_path / "work-queue"
    (wq / "archive" / "2026-01").mkdir(parents=True)
    (wq / "archive" / "2026-01" / "WRK-001.md").write_text(
        "---\nid: WRK-001\nstatus: done\n---\n# Done item\n",
        encoding="utf-8",
    )
    return wq
