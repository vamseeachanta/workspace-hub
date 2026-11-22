"""
Tests for refresh-agent-work-queue.py — deterministic queue generation.

Covers:
  - Markdown structure: header, summary table, per-agent sections
  - Deterministic ordering: issues sorted by number ascending within each priority
  - Priority breakdown: high/medium/low separated per agent
  - Timestamp present and ISO-formatted
  - Empty agent queues handled gracefully
  - Staleness detection: fresh vs stale vs missing file
  - Parity check: file counts vs live GitHub counts

Run: uv run --no-project python -m pytest tests/work-queue/test_queue_refresh.py -v
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
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
    "dispatch:ready,lane:agy": json.dumps([
        _make_issue(1769, "Phase B summarization - 394K docs", ["dispatch:ready", "lane:agy", "decision:research"]),
        _make_issue(1823, "Map 825 hydro functions to standards", ["dispatch:ready", "lane:agy", "decision:ecosystem"]),
    ]),
    "dispatch:ready,lane:claude": json.dumps([
        _make_issue(1811, "Promote SN curve POC v2", ["dispatch:ready", "lane:claude", "decision:engineering"]),
        _make_issue(1839, "Workflow hard-stops", ["dispatch:ready", "lane:claude", "decision:ecosystem"]),
        _make_issue(1857, "Rolling 1-week label queue", ["dispatch:ready", "lane:claude", "decision:throughput"]),
    ]),
    "dispatch:ready,lane:codex": json.dumps([
        _make_issue(1748, "Convert agents to SKILL.md", ["dispatch:ready", "lane:codex", "decision:ecosystem"]),
        _make_issue(1824, "Uplift test coverage 2.95% to 20%", ["dispatch:ready", "lane:codex", "decision:throughput"]),
        _make_issue(1830, "Review solver queue bugs", ["dispatch:ready", "lane:codex", "decision:engineering"]),
    ]),
}


def mock_subprocess_run(cmd, **kwargs):
    """Mock gh issue list calls, returning canned JSON."""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

    # Match --label "dispatch:ready,lane:X" patterns
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
        assert queue_output.startswith("# Label Work Queue")

    def test_has_summary_table(self, queue_output: str):
        assert "## Queue Summary" in queue_output
        assert "| Lane" in queue_output

    def test_has_agy_section(self, queue_output: str):
        assert "## Agy Queue" in queue_output

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

    def test_agy_high_sorted(self, queue_output: str):
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

    def test_agy_count(self, queue_output: str):
        assert "| **AGY**" in queue_output
        # Find the Agy row and check ready count is 2
        for line in queue_output.splitlines():
            if "**AGY**" in line:
                assert "| 2 |" in line
                break

    def test_claude_count(self, queue_output: str):
        for line in queue_output.splitlines():
            if "**CLAUDE**" in line:
                assert "| 3 |" in line
                break

    def test_codex_count(self, queue_output: str):
        for line in queue_output.splitlines():
            if "**CODEX**" in line:
                assert "| 3 |" in line
                break


# ── Label section tests ─────────────────────────────────────────────────


class TestLaneSections:
    """Each lane section should list dispatch:ready issues."""

    def test_agy_has_ready_issues(self, queue_output: str):
        agy_start = queue_output.index("## Agy Queue")
        claude_start = queue_output.index("## Claude Queue")
        agy_section = queue_output[agy_start:claude_start]
        assert "#1769" in agy_section
        assert "#1823" in agy_section


# ── Edge case tests ─────────────────────────────────────────────────────


class TestEdgeCases:
    """Empty queues and missing data handled gracefully."""

    def test_empty_low_priority_no_crash(self, queue_output: str):
        assert queue_output is not None
        assert len(queue_output) > 100

    def test_no_pipe_characters_unescaped_in_titles(self, queue_output: str):
        # Issue titles containing special chars should be safe in markdown tables
        assert "Review solver queue bugs" not in queue_output
        assert "| #1830 | [withheld; see issue] |" in queue_output


# Focus cap source: issues/2052, default five high-priority issues per agent.
# Independent synthetic example: high issues are 11, 13, 14, 17, 18, 19;
# medium 1, low 2 and unlabelled 3 are excluded. Repeated 11 counts once.
# Thus default selects 11, 13, 14, 17, 18; cap two selects 11, 13;
# cap six or twenty selects all six; zero selects none. IDs are fixture data.
FOCUS_ISSUES = [
    _make_issue(19, "Synthetic final task", ["priority:high"]),
    _make_issue(2, "Synthetic low task", ["priority:low"]),
    _make_issue(17, "Synthetic later task", ["priority:high"]),
    _make_issue(11, "Synthetic first task", ["priority:high"]),
    _make_issue(1, "Synthetic medium task", ["priority:medium"]),
    _make_issue(18, "Synthetic next task", ["priority:high"]),
    _make_issue(14, "Synthetic middle task", ["priority:high"]),
    _make_issue(3, "Synthetic unlabelled task", []),
    _make_issue(13, "Synthetic second task", ["priority:high"]),
    _make_issue(11, "Synthetic first task", ["priority:high"]),
]
# Fixed synthetic clock, independent of the system clock.
FOCUS_NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)


@pytest.fixture
def focus_module(monkeypatch):
    import importlib

    monkeypatch.syspath_prepend(os.path.join(REPO_ROOT, "scripts"))
    mod = importlib.import_module("refresh-agent-work-queue")
    monkeypatch.setattr(mod, "LANES", [
        {"name": "Test", "key": "TEST", "label": "queue:test", "role": "Testing"},
    ])
    return mod


def _focus_numbers(markdown):
    return re.findall(r"^\d+\. #(\d+)\b", markdown, re.MULTILINE)


class TestWeeklyFocus:
    def test_default_cap_and_table_preservation(self, focus_module):
        queries = []

        def query(labels):
            queries.append(labels)
            return FOCUS_ISSUES

        output = focus_module.generate_queue_markdown(query_fn=query, now=FOCUS_NOW)
        assert queries == ["dispatch:ready,queue:test"]
        assert _focus_numbers(output) == ["11", "13", "14", "17", "18"]
        # Existing table keeps every row, ascending, including the repeated 11.
        assert re.findall(r"^\| \d+ \| #(\d+) \|", output, re.MULTILINE) == [
            "1", "2", "3", "11", "11", "13", "14", "17", "18", "19",
        ]
        assert output.index("### This Week's Focus") > output.index("| 10 | #19 |")
        assert "Last refresh: 2026-10-15T00:00:00Z" in output

    @pytest.mark.parametrize(("cap", "expected"), [
        (2, ["11", "13"]),
        (0, []),
        (20, ["11", "13", "14", "17", "18", "19"]),
    ])
    def test_configured_cap(self, focus_module, cap, expected):
        output = focus_module.generate_queue_markdown(
            query_fn=lambda _: FOCUS_ISSUES, now=FOCUS_NOW, focus_limit=cap,
        )
        assert _focus_numbers(output) == expected

    def test_deterministic_ties_and_no_duplicates(self, focus_module):
        def render(issues):
            return focus_module.generate_queue_markdown(
                query_fn=lambda _: issues, now=FOCUS_NOW, focus_limit=6,
            )

        output = render(FOCUS_ISSUES)
        assert output == render(FOCUS_ISSUES)
        assert output == render(list(reversed(FOCUS_ISSUES)))
        assert _focus_numbers(output) == ["11", "13", "14", "17", "18", "19"]

    @pytest.mark.parametrize("issues", [[], FOCUS_ISSUES[1:2]])
    def test_empty_focus(self, focus_module, issues):
        output = focus_module.generate_queue_markdown(
            query_fn=lambda _: issues, now=FOCUS_NOW,
        )
        assert "### This Week's Focus\n\n_No high-priority issues._" in output
        assert _focus_numbers(output) == []
        if not issues:
            assert "| # | Issue | Title |" not in output

    def test_reasons_keep_publication_boundary(self, focus_module):
        issue = _make_issue(11, "Unpublishable synthetic title", [
            "priority:high", "sensitive:unpublishable-metadata",
        ])
        output = focus_module.generate_queue_markdown(
            query_fn=lambda _: [issue], now=FOCUS_NOW,
        )
        assert "Unpublishable synthetic title" not in output
        assert "unpublishable-metadata" not in output
        assert (
            "1. #11 — [withheld; see issue] — High priority: needs attention this week."
        ) in output

    def test_cap_applies_to_each_section(self, focus_module, monkeypatch):
        monkeypatch.setattr(focus_module, "LANES", [
            {"name": "First", "key": "FIRST", "label": "queue:first", "role": "Testing"},
            {"name": "Second", "key": "SECOND", "label": "queue:second", "role": "Testing"},
        ])
        output = focus_module.generate_queue_markdown(
            query_fn=lambda _: FOCUS_ISSUES, now=FOCUS_NOW, focus_limit=2,
        )
        # Each independent fixture query selects 11, 13 by the example above.
        assert _focus_numbers(output) == ["11", "13", "11", "13"]

    def test_negative_cap_rejected(self, focus_module):
        # A count below zero is invalid; zero is the documented disable value.
        with pytest.raises(ValueError, match="non-negative"):
            focus_module.generate_queue_markdown(
                query_fn=lambda _: FOCUS_ISSUES, now=FOCUS_NOW, focus_limit=-1,
            )

    def test_command_line_cap(self, focus_module, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", [SCRIPT, "--dry-run", "--focus-limit", "2"])
        monkeypatch.setattr(focus_module, "gh_query_issues", lambda _: FOCUS_ISSUES)
        focus_module.main()
        assert _focus_numbers(capsys.readouterr().out) == ["11", "13"]


# ── Staleness detection tests ──────────────────────────────────────────


class TestStalenessDetection:
    """check_staleness reports whether the queue file is outdated."""

    @pytest.fixture(autouse=True)
    def _load_module(self, tmp_path):
        sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
        try:
            import importlib
            self.mod = importlib.import_module("refresh-agent-work-queue")
        finally:
            sys.path.pop(0)
        self.tmp_path = tmp_path

    def _write_queue(self, timestamp_str: str) -> Path:
        p = self.tmp_path / "agent-work-queue.md"
        p.write_text(f"# Queue\n\n*Last refresh: {timestamp_str}*\n")
        return p

    def test_fresh_file_not_stale(self):
        from datetime import datetime, timezone, timedelta
        now = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        qf = self._write_queue(ts)
        result = self.mod.check_staleness(queue_file=qf, now=now)
        assert result["stale"] is False
        assert result["age_days"] == 2.0

    def test_old_file_is_stale(self):
        from datetime import datetime, timezone, timedelta
        now = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
        ts = (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        qf = self._write_queue(ts)
        result = self.mod.check_staleness(queue_file=qf, now=now)
        assert result["stale"] is True
        assert result["age_days"] == 10.0

    def test_missing_file_is_stale(self):
        from datetime import datetime, timezone
        now = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
        qf = self.tmp_path / "nonexistent.md"
        result = self.mod.check_staleness(queue_file=qf, now=now)
        assert result["stale"] is True
        assert "not found" in result["message"]

    def test_no_timestamp_is_stale(self):
        from datetime import datetime, timezone
        now = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
        qf = self.tmp_path / "no-ts.md"
        qf.write_text("# Queue\nNo timestamp here.\n")
        result = self.mod.check_staleness(queue_file=qf, now=now)
        assert result["stale"] is True
        assert "No timestamp" in result["message"]


# ── Parity check tests ────────────────────────────────────────────────


class TestParityCheck:
    """parity_check compares file issue counts against live query results."""

    @pytest.fixture(autouse=True)
    def _load_module(self, tmp_path):
        sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
        try:
            import importlib
            self.mod = importlib.import_module("refresh-agent-work-queue")
        finally:
            sys.path.pop(0)
        self.tmp_path = tmp_path

    def _write_summary_table(self, agy: int, claude: int, codex: int) -> Path:
        p = self.tmp_path / "agent-work-queue.md"
        lines = [
            "# Agent Work Queue",
            "",
            "## Queue Summary",
            "",
            "| Lane | Ready | Label |",
            "|------|-------|-------|",
            f"| **AGY** | {agy} | `lane:agy` |",
            f"| **CLAUDE** | {claude} | `lane:claude` |",
            f"| **CODEX** | {codex} | `lane:codex` |",
        ]
        p.write_text("\n".join(lines))
        return p

    def test_parity_when_counts_match(self):
        qf = self._write_summary_table(2, 3, 3)

        def mock_query(labels):
            counts = {
                "dispatch:ready,lane:agy": 2,
                "dispatch:ready,lane:claude": 3,
                "dispatch:ready,lane:codex": 3,
            }
            n = counts.get(labels, 0)
            return [{"number": i, "title": f"Issue {i}", "labels": []} for i in range(n)]

        result = self.mod.parity_check(queue_file=qf, query_fn=mock_query)
        assert result["parity"] is True

    def test_drift_detected_when_counts_differ(self):
        qf = self._write_summary_table(2, 3, 3)

        def mock_query(labels):
            # Claude has 5 live issues instead of 3
            counts = {
                "dispatch:ready,lane:agy": 2,
                "dispatch:ready,lane:claude": 5,
                "dispatch:ready,lane:codex": 3,
            }
            n = counts.get(labels, 0)
            return [{"number": i, "title": f"Issue {i}", "labels": []} for i in range(n)]

        result = self.mod.parity_check(queue_file=qf, query_fn=mock_query)
        assert result["parity"] is False
        assert len(result["drifted_agents"]) == 1
        assert result["drifted_agents"][0]["agent"] == "CLAUDE"
        assert result["drifted_agents"][0]["delta"] == 2

    def test_missing_file_fails_parity(self):
        qf = self.tmp_path / "nonexistent.md"
        result = self.mod.parity_check(queue_file=qf, query_fn=lambda l: [])
        assert result["parity"] is False
