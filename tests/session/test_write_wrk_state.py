"""
ABOUTME: Unit tests for write-wrk-state.py — WRK frontmatter session_state persistence
ABOUTME: Tests frontmatter parsing, state merging, serialization, and error handling
"""

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

# Import the hyphen-named module via importlib (Python cannot import 'a-b' directly)
_MODULE_PATH = (
    Path(__file__).parent.parent.parent / "scripts" / "session" / "write-wrk-state.py"
)
_spec = importlib.util.spec_from_file_location("write_wrk_state", _MODULE_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

build_session_state = _mod.build_session_state
parse_csv_arg = _mod.parse_csv_arg
parse_frontmatter = _mod.parse_frontmatter
parse_newline_arg = _mod.parse_newline_arg
render_frontmatter = _mod.render_frontmatter
write_state = _mod.write_state


# ─── Fixtures ─────────────────────────────────────────────────────────────────

WRK_FIXTURE_MINIMAL = textwrap.dedent("""\
    ---
    id: WRK-999
    title: Test item
    status: pending
    computer: ace-linux-1
    percent_complete: 0
    ---

    # Test item body

    Some markdown content here.
""")

WRK_FIXTURE_WITH_STATE = textwrap.dedent("""\
    ---
    id: WRK-888
    title: Existing state item
    status: working
    computer: ace-linux-1
    percent_complete: 50
    session_state:
      last_updated: 2026-01-01T00:00:00Z
      progress_notes: Old notes
      modified_files:
      - old-file.py
      next_steps:
      - Old step
      recent_commits: ''
    ---

    # Existing state item body
""")

WRK_FIXTURE_NO_FRONTMATTER = textwrap.dedent("""\
    # No frontmatter here

    Just a plain markdown file without YAML frontmatter.
""")


# ─── parse_frontmatter ────────────────────────────────────────────────────────

class TestParseFrontmatter:
    def test_parse_valid_frontmatter_returns_dict_and_body(self):
        data, body = parse_frontmatter(WRK_FIXTURE_MINIMAL)
        assert data["id"] == "WRK-999"
        assert data["status"] == "pending"
        assert "# Test item body" in body

    def test_parse_returns_empty_dict_when_no_frontmatter(self):
        data, body = parse_frontmatter(WRK_FIXTURE_NO_FRONTMATTER)
        assert data == {}
        assert "plain markdown" in body

    def test_parse_preserves_all_existing_keys(self):
        data, _ = parse_frontmatter(WRK_FIXTURE_WITH_STATE)
        assert data["percent_complete"] == 50
        # PyYAML parses ISO-8601 timestamps as datetime objects; assert the date component
        import datetime  # noqa: PLC0415
        last_updated = data["session_state"]["last_updated"]
        if isinstance(last_updated, datetime.datetime):
            assert last_updated.year == 2026
            assert last_updated.month == 1
            assert last_updated.day == 1
        else:
            assert "2026-01-01" in str(last_updated)

    def test_parse_handles_empty_string(self):
        data, body = parse_frontmatter("")
        assert data == {}
        assert body == ""


# ─── render_frontmatter ───────────────────────────────────────────────────────

class TestRenderFrontmatter:
    def test_render_produces_yaml_block(self):
        data = {"id": "WRK-999", "status": "pending"}
        result = render_frontmatter(data)
        assert result.startswith("---\n")
        assert result.endswith("---\n")

    def test_render_round_trips_data(self):
        data = {"id": "WRK-123", "title": "My task", "percent_complete": 42}
        rendered = render_frontmatter(data)
        parsed = yaml.safe_load(rendered.strip("---\n"))
        assert parsed["id"] == "WRK-123"
        assert parsed["percent_complete"] == 42

    def test_render_allows_unicode(self):
        data = {"title": "Test with unicode: \u00e9\u00e0\u00fc"}
        result = render_frontmatter(data)
        assert "\u00e9" in result


# ─── build_session_state ──────────────────────────────────────────────────────

class TestBuildSessionState:
    def test_returns_expected_keys(self):
        state = build_session_state(
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="Did step 1",
            modified_files=["scripts/foo.py"],
            next_steps=["Step 2", "Step 3"],
            recent_commits="abc1234 feat: something",
        )
        assert "last_updated" in state
        assert "progress_notes" in state
        assert "modified_files" in state
        assert "next_steps" in state
        assert "recent_commits" in state

    def test_filters_empty_modified_files(self):
        state = build_session_state(
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="",
            modified_files=["", "real-file.py", ""],
            next_steps=[],
            recent_commits="",
        )
        assert state["modified_files"] == ["real-file.py"]

    def test_filters_empty_next_steps(self):
        state = build_session_state(
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="",
            modified_files=[],
            next_steps=["", "Step A", ""],
            recent_commits="",
        )
        assert state["next_steps"] == ["Step A"]

    def test_empty_progress_notes_gets_default_message(self):
        state = build_session_state(
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="   ",
            modified_files=[],
            next_steps=[],
            recent_commits="",
        )
        assert state["progress_notes"] == "No notes captured."


# ─── write_state ─────────────────────────────────────────────────────────────

class TestWriteState:
    @pytest.fixture
    def minimal_wrk_file(self, tmp_path):
        f = tmp_path / "WRK-999.md"
        f.write_text(WRK_FIXTURE_MINIMAL, encoding="utf-8")
        return f

    @pytest.fixture
    def existing_state_wrk_file(self, tmp_path):
        f = tmp_path / "WRK-888.md"
        f.write_text(WRK_FIXTURE_WITH_STATE, encoding="utf-8")
        return f

    def test_write_state_adds_session_state_block(self, minimal_wrk_file):
        write_state(
            wrk_path=str(minimal_wrk_file),
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="Completed step 1",
            modified_files=["scripts/session/refresh-context.sh"],
            next_steps=["Run tests", "Commit"],
            recent_commits="abc1234 feat: initial",
        )
        content = minimal_wrk_file.read_text(encoding="utf-8")
        assert "session_state:" in content
        assert "Completed step 1" in content
        assert "Run tests" in content

    def test_write_state_preserves_existing_frontmatter_keys(self, minimal_wrk_file):
        write_state(
            wrk_path=str(minimal_wrk_file),
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="Step done",
            modified_files=[],
            next_steps=[],
            recent_commits="",
        )
        content = minimal_wrk_file.read_text(encoding="utf-8")
        data, _ = parse_frontmatter(content)
        assert data["id"] == "WRK-999"
        assert data["status"] == "pending"
        assert data["computer"] == "ace-linux-1"

    def test_write_state_overwrites_previous_session_state(self, existing_state_wrk_file):
        write_state(
            wrk_path=str(existing_state_wrk_file),
            last_updated="2026-02-24T08:00:00Z",
            progress_notes="Updated notes",
            modified_files=["new-file.py"],
            next_steps=["New step"],
            recent_commits="def5678 fix: bug",
        )
        content = existing_state_wrk_file.read_text(encoding="utf-8")
        data, _ = parse_frontmatter(content)
        assert data["session_state"]["last_updated"] == "2026-02-24T08:00:00Z"
        assert data["session_state"]["progress_notes"] == "Updated notes"
        assert "old-file.py" not in str(data["session_state"]["modified_files"])

    def test_write_state_preserves_markdown_body(self, minimal_wrk_file):
        write_state(
            wrk_path=str(minimal_wrk_file),
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="",
            modified_files=[],
            next_steps=[],
            recent_commits="",
        )
        content = minimal_wrk_file.read_text(encoding="utf-8")
        assert "# Test item body" in content
        assert "Some markdown content here." in content

    def test_write_state_raises_for_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            write_state(
                wrk_path=str(tmp_path / "NONEXISTENT.md"),
                last_updated="2026-02-24T07:00:00Z",
                progress_notes="",
                modified_files=[],
                next_steps=[],
                recent_commits="",
            )

    def test_write_state_handles_file_without_frontmatter(self, tmp_path):
        f = tmp_path / "WRK-plain.md"
        f.write_text(WRK_FIXTURE_NO_FRONTMATTER, encoding="utf-8")
        # Should not raise; session_state gets embedded in new frontmatter
        write_state(
            wrk_path=str(f),
            last_updated="2026-02-24T07:00:00Z",
            progress_notes="Added retroactively",
            modified_files=[],
            next_steps=[],
            recent_commits="",
        )
        content = f.read_text(encoding="utf-8")
        assert "session_state:" in content


# ─── parse_csv_arg / parse_newline_arg ────────────────────────────────────────

class TestParseArgs:
    def test_parse_csv_splits_on_comma(self):
        result = parse_csv_arg("a.py,b.py,c.py")
        assert result == ["a.py", "b.py", "c.py"]

    def test_parse_csv_strips_whitespace(self):
        result = parse_csv_arg(" a.py , b.py ")
        assert result == ["a.py", "b.py"]

    def test_parse_csv_ignores_empty_segments(self):
        result = parse_csv_arg(",a.py,,b.py,")
        assert result == ["a.py", "b.py"]

    def test_parse_csv_returns_empty_list_for_empty_string(self):
        assert parse_csv_arg("") == []

    def test_parse_newline_splits_on_newlines(self):
        result = parse_newline_arg("Step 1\nStep 2\nStep 3")
        assert result == ["Step 1", "Step 2", "Step 3"]

    def test_parse_newline_strips_blank_lines(self):
        result = parse_newline_arg("Step 1\n\nStep 2\n")
        assert result == ["Step 1", "Step 2"]

    def test_parse_newline_returns_empty_list_for_empty_string(self):
        assert parse_newline_arg("") == []
