"""Tests for GitHub Issue integration in start_stage / exit_stage.

WRK-1333: Wire update-github-issue.py into stage lifecycle.
"""
from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Ensure scripts/work-queue is importable
_SCRIPT_DIR = str(Path(__file__).parent.parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


# ── Helper: create a minimal WRK file with frontmatter ──────────────────────

def _create_wrk_file(
    tmp_path: Path, wrk_id: str, github_issue_ref: str | None = None,
) -> Path:
    """Create a minimal WRK .md file with optional github_issue_ref."""
    queue_dir = tmp_path / ".claude" / "work-queue" / "working"
    queue_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"id: {wrk_id}",
        f"title: Test item",
        "status: working",
    ]
    if github_issue_ref:
        lines.append(f"github_issue_ref: {github_issue_ref}")
    lines.append("---")
    lines.append("")
    lines.append("Body text here.")
    wrk_file = queue_dir / f"{wrk_id}.md"
    wrk_file.write_text("\n".join(lines))
    return wrk_file


# ── _get_github_issue_ref tests ──────────────────────────────────────────────

def test_get_github_issue_ref_returns_url(tmp_path):
    """_get_github_issue_ref returns URL when github_issue_ref present."""
    from start_stage import _get_github_issue_ref
    url = "https://github.com/owner/repo/issues/42"
    _create_wrk_file(tmp_path, "WRK-100", github_issue_ref=url)
    result = _get_github_issue_ref("WRK-100", str(tmp_path))
    assert result == url


def test_get_github_issue_ref_returns_none_when_absent(tmp_path):
    """_get_github_issue_ref returns None when no github_issue_ref."""
    from start_stage import _get_github_issue_ref
    _create_wrk_file(tmp_path, "WRK-101")
    result = _get_github_issue_ref("WRK-101", str(tmp_path))
    assert result is None


def test_get_github_issue_ref_returns_none_when_no_file(tmp_path):
    """_get_github_issue_ref returns None when WRK file not found."""
    from start_stage import _get_github_issue_ref
    result = _get_github_issue_ref("WRK-999", str(tmp_path))
    assert result is None


# ── _regenerate_lifecycle_html (now calls update-github-issue.py) ────────────

@patch("start_stage.subprocess.run")
def test_regenerate_calls_update_script(mock_run, tmp_path):
    """_regenerate_lifecycle_html calls update-github-issue.py --update."""
    from start_stage import _regenerate_lifecycle_html

    url = "https://github.com/owner/repo/issues/42"
    _create_wrk_file(tmp_path, "WRK-200", github_issue_ref=url)

    # Create the update script so the existence check passes
    script_path = tmp_path / "scripts" / "knowledge" / "update-github-issue.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("# stub")

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    _regenerate_lifecycle_html("WRK-200", str(tmp_path))

    # Verify it called update-github-issue.py with --update
    assert mock_run.called
    found = any(
        "update-github-issue.py" in str(c) and "--update" in str(c)
        for c in mock_run.call_args_list
    )
    assert found, f"Expected update-github-issue.py --update call, got: {mock_run.call_args_list}"


@patch("start_stage.subprocess.run")
def test_regenerate_skips_if_no_issue_ref(mock_run, tmp_path):
    """_regenerate_lifecycle_html silently skips when no github_issue_ref."""
    from start_stage import _regenerate_lifecycle_html

    _create_wrk_file(tmp_path, "WRK-201")  # no github_issue_ref

    # Script exists but should not be called
    script_path = tmp_path / "scripts" / "knowledge" / "update-github-issue.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("# stub")

    _regenerate_lifecycle_html("WRK-201", str(tmp_path))

    # Should NOT have called update-github-issue.py
    for c in mock_run.call_args_list:
        assert "update-github-issue.py" not in str(c), \
            f"Should not call update script without issue ref, but called: {c}"


# ── _open_html_stage1 tests ─────────────────────────────────────────────────

@patch("start_stage.subprocess.Popen")
def test_open_stage1_uses_issue_url(mock_popen, tmp_path):
    """_open_html_stage1 opens GitHub Issue URL when github_issue_ref present."""
    from start_stage import _open_html_stage1

    url = "https://github.com/owner/repo/issues/42"
    _create_wrk_file(tmp_path, "WRK-300", github_issue_ref=url)

    _open_html_stage1("WRK-300", str(tmp_path))

    # Should have opened the URL via xdg-open
    assert mock_popen.called
    first_call_args = mock_popen.call_args_list[0]
    cmd = first_call_args[0][0] if first_call_args[0] else first_call_args[1].get("args", [])
    assert cmd[0] == "xdg-open"
    assert cmd[1] == url


@patch("start_stage.subprocess.run")
@patch("start_stage.subprocess.Popen")
def test_open_stage1_falls_back_to_html(mock_popen, mock_run, tmp_path):
    """_open_html_stage1 falls back to HTML when no github_issue_ref."""
    from start_stage import _open_html_stage1

    _create_wrk_file(tmp_path, "WRK-301")  # no github_issue_ref

    # Create HTML files for fallback
    assets_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-301"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "WRK-301-lifecycle.html").write_text("<html>lifecycle</html>")
    (assets_dir / "WRK-301-plan.html").write_text("<html>plan</html>")

    # generate-html-review.py must exist for fallback path
    gen_script = tmp_path / "scripts" / "work-queue" / "generate-html-review.py"
    gen_script.parent.mkdir(parents=True, exist_ok=True)
    gen_script.write_text("# stub")
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    _open_html_stage1("WRK-301", str(tmp_path))

    # Should have opened HTML files (not a URL)
    assert mock_popen.called
    opened_paths = [
        c[0][0][1] if c[0] else c[1].get("args", ["", ""])[1]
        for c in mock_popen.call_args_list
    ]
    assert any("lifecycle.html" in p for p in opened_paths), \
        f"Expected HTML fallback, opened: {opened_paths}"


# ── exit_stage _regenerate_lifecycle_html ────────────────────────────────────

@patch("subprocess.run")
def test_exit_stage_updates_issue(mock_run, tmp_path):
    """exit_stage._regenerate_lifecycle_html calls update-github-issue.py."""
    import exit_stage

    url = "https://github.com/owner/repo/issues/55"
    _create_wrk_file(tmp_path, "WRK-400", github_issue_ref=url)

    script_path = tmp_path / "scripts" / "knowledge" / "update-github-issue.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("# stub")

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    exit_stage._regenerate_lifecycle_html("WRK-400", str(tmp_path))

    found = any(
        "update-github-issue.py" in str(c) and "--update" in str(c)
        for c in mock_run.call_args_list
    )
    assert found, f"Expected update-github-issue.py --update call, got: {mock_run.call_args_list}"
