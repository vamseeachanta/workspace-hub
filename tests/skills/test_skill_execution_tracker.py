"""TDD tests for skill-execution-tracker.py (WRK-5086)."""
import json
import tempfile
from pathlib import Path

import pytest

# Module under test — imported after writing implementation
from scripts.skills.skill_execution_tracker import (
    parse_session_log,
    extract_skill_invocations,
    write_executions_jsonl,
)


@pytest.fixture
def sample_session_log(tmp_path):
    """Create a sample session JSONL with skill invocations."""
    log_file = tmp_path / "session_20260315.jsonl"
    entries = [
        # Skill tool invocation (pre + post pair)
        {"ts": "2026-03-15T10:00:00-05:00", "epoch": 1773500000, "hook": "pre", "tool": "Skill", "project": "workspace-hub", "repo": "workspace-hub"},
        {"ts": "2026-03-15T10:00:01-05:00", "epoch": 1773500001, "hook": "post", "tool": "Skill", "project": "workspace-hub", "repo": "workspace-hub"},
        # Read of a SKILL.md file
        {"ts": "2026-03-15T10:01:00-05:00", "epoch": 1773500060, "hook": "pre", "tool": "Read", "project": "workspace-hub", "repo": "workspace-hub", "file": "/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/work-queue/SKILL.md"},
        {"ts": "2026-03-15T10:01:01-05:00", "epoch": 1773500061, "hook": "post", "tool": "Read", "project": "workspace-hub", "repo": "workspace-hub", "file": "/mnt/local-analysis/workspace-hub/.claude/skills/workspace-hub/work-queue/SKILL.md"},
        # Non-skill Read (should be ignored)
        {"ts": "2026-03-15T10:02:00-05:00", "epoch": 1773500120, "hook": "pre", "tool": "Read", "project": "workspace-hub", "repo": "workspace-hub", "file": "/mnt/local-analysis/workspace-hub/CLAUDE.md"},
        {"ts": "2026-03-15T10:02:01-05:00", "epoch": 1773500121, "hook": "post", "tool": "Read", "project": "workspace-hub", "repo": "workspace-hub", "file": "/mnt/local-analysis/workspace-hub/CLAUDE.md"},
        # Bash command (should be ignored)
        {"ts": "2026-03-15T10:03:00-05:00", "epoch": 1773500180, "hook": "pre", "tool": "Bash", "project": "workspace-hub", "repo": "workspace-hub", "cmd": "git status"},
        {"ts": "2026-03-15T10:03:01-05:00", "epoch": 1773500181, "hook": "post", "tool": "Bash", "project": "workspace-hub", "repo": "workspace-hub", "cmd": "git status"},
        # Another Skill tool invocation
        {"ts": "2026-03-15T10:05:00-05:00", "epoch": 1773500300, "hook": "pre", "tool": "Skill", "project": "workspace-hub", "repo": "workspace-hub"},
        {"ts": "2026-03-15T10:05:02-05:00", "epoch": 1773500302, "hook": "post", "tool": "Skill", "project": "workspace-hub", "repo": "workspace-hub"},
    ]
    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return log_file


@pytest.fixture
def empty_session_log(tmp_path):
    """Create an empty session log."""
    log_file = tmp_path / "session_20260301.jsonl"
    log_file.write_text("")
    return log_file


class TestParseSessionLog:
    def test_parses_valid_jsonl(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        assert len(entries) == 10

    def test_empty_file_returns_empty_list(self, empty_session_log):
        entries = parse_session_log(empty_session_log)
        assert entries == []

    def test_malformed_lines_skipped(self, tmp_path):
        log_file = tmp_path / "session_bad.jsonl"
        log_file.write_text('{"ts":"2026-03-15","hook":"pre","tool":"Skill"}\nNOT JSON\n{"ts":"2026-03-15","hook":"post","tool":"Skill"}\n')
        entries = parse_session_log(log_file)
        assert len(entries) == 2


class TestExtractSkillInvocations:
    def test_finds_skill_tool_invocations(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test-session")
        # Should find: 2 Skill tool invocations + 1 SKILL.md Read = 3
        assert len(invocations) == 3

    def test_ignores_non_skill_entries(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test-session")
        # No Bash or non-skill Read entries should be in results
        tools = [inv["skill_name"] for inv in invocations]
        assert "Bash" not in tools
        assert "CLAUDE.md" not in str(tools)

    def test_extracts_skill_name_from_read_path(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test-session")
        skill_names = [inv["skill_name"] for inv in invocations]
        assert "work-queue" in skill_names

    def test_output_schema_fields(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test-session")
        required_fields = {"skill_name", "timestamp", "session_id", "project", "duration_s"}
        for inv in invocations:
            assert required_fields.issubset(set(inv.keys())), f"Missing fields: {required_fields - set(inv.keys())}"

    def test_session_id_attached(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="abc-123")
        for inv in invocations:
            assert inv["session_id"] == "abc-123"

    def test_duration_calculated(self, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test")
        # Skill tool: epoch 1773500000 to 1773500001 = 1s
        skill_invs = [i for i in invocations if i["skill_name"] == "Skill"]
        assert skill_invs[0]["duration_s"] == 1

    def test_empty_entries_returns_empty(self):
        invocations = extract_skill_invocations([], session_id="test")
        assert invocations == []


class TestWriteExecutionsJsonl:
    def test_writes_valid_jsonl(self, tmp_path, sample_session_log):
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test")
        output = tmp_path / "skill-executions.jsonl"
        write_executions_jsonl(invocations, output)
        lines = output.read_text().strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "skill_name" in parsed

    def test_appends_to_existing(self, tmp_path, sample_session_log):
        output = tmp_path / "skill-executions.jsonl"
        output.write_text('{"skill_name":"existing","timestamp":"2026-03-14"}\n')
        entries = parse_session_log(sample_session_log)
        invocations = extract_skill_invocations(entries, session_id="test")
        write_executions_jsonl(invocations, output)
        lines = output.read_text().strip().split("\n")
        assert len(lines) == 4  # 1 existing + 3 new
        assert json.loads(lines[0])["skill_name"] == "existing"

    def test_empty_invocations_no_write(self, tmp_path):
        output = tmp_path / "skill-executions.jsonl"
        write_executions_jsonl([], output)
        assert not output.exists()
