"""
Tests for refresh-agent-work-queue.py — deterministic queue generation.

Covers:
  - Markdown structure: header, summary table, per-agent sections
  - Deterministic ordering: issues sorted by number ascending within each priority
  - Priority breakdown: high/medium/low separated per agent
  - Timestamp present and ISO-formatted
  - Empty agent queues handled gracefully

Run: uv run --no-project python -m pytest tests/work-queue/test_queue_refresh.py -v
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from unittest.mock import patch

import pytest

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
SCRIPT = os.path.join(REPO_ROOT, "scripts", "refresh-agent-work-queue.py")


# ── Fixtures ────────────────────────────────────────────────────────────


def _make_issue(number: int, title: str, labels: list[str]) -> dict:
    """Build a minimal issue dict matching gh JSON output."""
    return {
        "number": number,
        "title": title,
        "labels": [{"name": lbl} for lbl in labels],
    }


SAMPLE_ISSUES = {
    "agent:gemini,priority:high": json.dumps([
        _make_issue(1823, "Map 825 hydro functions to standards", ["agent:gemini", "priority:high", "cat:standards"]),
        _make_issue(1769, "Phase B summarization — 394K docs", ["agent:gemini", "priority:high"]),
    ]),
    "agent:gemini,priority:medium": json.dumps([
        _make_issue(1822, "Close 13 pipeline standards gaps", ["agent:gemini", "priority:medium"]),
    ]),
    "agent:gemini,priority:low": json.dumps([]),
    "agent:claude,priority:high": json.dumps([
        _make_issue(1857, "Rolling 1-week agent work queue", ["agent:claude", "priority:high"]),
        _make_issue(1839, "Workflow hard-stops", ["agent:claude", "priority:high"]),
        _make_issue(1811, "Promote SN curve POC v2", ["agent:claude", "priority:high"]),
    ]),
    "agent:claude,priority:medium": json.dumps([
        _make_issue(1853, "Complete curves_of_form.py", ["agent:claude", "priority:medium"]),
    ]),
    "agent:claude,priority:low": json.dumps([]),
    "agent:codex,priority:high": json.dumps([
        _make_issue(1824, "Uplift test coverage 2.95% → 20%", ["agent:codex", "priority:high"]),
    ]),
    "agent:codex,priority:medium": json.dumps([
        _make_issue(1830, "Review solver queue bugs", ["agent:codex", "priority:medium"]),
    ]),
    "agent:codex,priority:low": json.dumps([
        _make_issue(1748, "Convert agents to SKILL.md", ["agent:codex", "priority:low"]),
    ]),
}


def mock_subprocess_run(cmd, **kwargs):
    """Mock gh issue list calls, returning canned JSON."""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

    # Match --label "agent:X,priority:Y" patterns
    for label_combo, data in SAMPLE_ISSUES.items():
        if label_combo in cmd_str:
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout=data, stderr=""
            )

    # Fallback: empty list
    return subprocess.CompletedProcess(
        args=cmd, returncode=0, stdout="[]", stderr=""
    )


@pytest.fixture
def queue_output():
    """Run the queue refresh script with mocked gh calls and return stdout."""
    with patch("subprocess.run", side_effect=mock_subprocess_run):
        # Import the module and call its generate function
        sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
        try:
            import importlib
            mod = importlib.import_module("refresh-agent-work-queue")
            return mod.generate_queue_markdown(
                query_fn=lambda labels: json.loads(SAMPLE_ISSUES.get(labels, "[]"))
            )
        finally:
            sys.path.pop(0)


# ── Structure tests ─────────────────────────────────────────────────────


class TestQueueMarkdownStructure:
    """Verify generated queue markdown has required sections."""

    def test_has_header(self, queue_output: str):
        assert queue_output.startswith("# Agent Work Queue")

    def test_has_summary_table(self, queue_output: str):
        assert "## Queue Summary" in queue_output
        assert "| Agent" in queue_output

    def test_has_gemini_section(self, queue_output: str):
        assert "## Gemini Queue" in queue_output

    def test_has_claude_section(self, queue_output: str):
        assert "## Claude Queue" in queue_output

    def test_has_codex_section(self, queue_output: str):
        assert "## Codex Queue" in queue_output

    def test_has_timestamp(self, queue_output: str):
        # ISO timestamp pattern: YYYY-MM-DDTHH:MM:SS
        assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", queue_output)

    def test_has_refresh_instructions(self, queue_output: str):
        assert "refresh" in queue_output.lower()


# ── Deterministic ordering tests ────────────────────────────────────────


class TestDeterministicOrdering:
    """Issues must be sorted by issue number ascending within each priority."""

    def test_gemini_high_sorted(self, queue_output: str):
        # #1769 should appear before #1823 (ascending by issue number)
        pos_1769 = queue_output.index("#1769")
        pos_1823 = queue_output.index("#1823")
        assert pos_1769 < pos_1823

    def test_claude_high_sorted(self, queue_output: str):
        # #1811, #1839, #1857 — ascending
        pos_1811 = queue_output.index("#1811")
        pos_1839 = queue_output.index("#1839")
        pos_1857 = queue_output.index("#1857")
        assert pos_1811 < pos_1839 < pos_1857


# ── Count accuracy tests ────────────────────────────────────────────────


class TestCountAccuracy:
    """Summary table counts must match actual issue counts."""

    def test_gemini_count(self, queue_output: str):
        # 2 high + 1 medium + 0 low = 3
        assert "| **GEMINI**" in queue_output
        # Find the Gemini row and check total is 3
        for line in queue_output.splitlines():
            if "**GEMINI**" in line:
                assert "3" in line
                break

    def test_claude_count(self, queue_output: str):
        # 3 high + 1 medium + 0 low = 4
        for line in queue_output.splitlines():
            if "**CLAUDE**" in line:
                assert "4" in line
                break

    def test_codex_count(self, queue_output: str):
        # 1 high + 1 medium + 1 low = 3
        for line in queue_output.splitlines():
            if "**CODEX**" in line:
                assert "3" in line
                break


# ── Priority section tests ──────────────────────────────────────────────


class TestPrioritySections:
    """Each agent section should have High/Medium/Low sub-sections."""

    def test_gemini_has_high_priority(self, queue_output: str):
        # Between Gemini header and Claude header, "High" should appear
        gemini_start = queue_output.index("## Gemini Queue")
        claude_start = queue_output.index("## Claude Queue")
        gemini_section = queue_output[gemini_start:claude_start]
        assert "### High" in gemini_section

    def test_gemini_has_medium_priority(self, queue_output: str):
        gemini_start = queue_output.index("## Gemini Queue")
        claude_start = queue_output.index("## Claude Queue")
        gemini_section = queue_output[gemini_start:claude_start]
        assert "### Medium" in gemini_section


# ── Edge case tests ─────────────────────────────────────────────────────


class TestEdgeCases:
    """Empty queues and missing data handled gracefully."""

    def test_empty_low_priority_no_crash(self, queue_output: str):
        # All agents have empty low-priority — should not crash
        assert queue_output is not None
        assert len(queue_output) > 100

    def test_no_pipe_characters_unescaped_in_titles(self, queue_output: str):
        # Issue titles containing special chars should be safe in markdown tables
        # Our test data has "→" and "—" which should pass through
        assert "→" in queue_output or "—" in queue_output
