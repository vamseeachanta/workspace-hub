"""Tests for auto-open lifecycle HTML at human-gate stages."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent dir to path so we can import start_stage
sys.path.insert(0, str(Path(__file__).parent.parent))

from start_stage import _auto_open_html_for_human_gates


@pytest.fixture
def tmp_wrk(tmp_path):
    """Set up a minimal WRK assets structure with HTML files."""
    assets = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-9999"
    evidence = assets / "evidence"
    evidence.mkdir(parents=True)
    # Create both HTML files
    (assets / "WRK-9999-lifecycle.html").write_text("<html>lifecycle</html>")
    (assets / "WRK-9999-plan.html").write_text("<html>plan</html>")
    # Create dummy browser-open script
    scripts_dir = tmp_path / "scripts" / "work-queue"
    scripts_dir.mkdir(parents=True)
    script = scripts_dir / "log-user-review-browser-open.sh"
    script.write_text("#!/usr/bin/env bash\n# dummy\n")
    script.chmod(0o755)
    return tmp_path


def _make_evidence(tmp_path, stages):
    """Write a user-review-browser-open.yaml with events for given stages."""
    ev_dir = tmp_path / ".claude" / "work-queue" / "assets" / "WRK-9999" / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    lines = ["events:\n"]
    for s in stages:
        lines.append(f"  - stage: {s}\n")
        lines.append(f"    opened_in_default_browser: true\n")
        lines.append(f"    html_ref: dummy.html\n")
        lines.append(f"    opened_at: '2026-01-01T00:00:00Z'\n")
        lines.append(f"    reviewer: test\n")
    (ev_dir / "user-review-browser-open.yaml").write_text("".join(lines))


class TestSkipsNonHumanGateStages:
    """Stages 2, 3, 8, 12 should not trigger any subprocess calls."""

    @pytest.mark.parametrize("stage", [2, 3, 8, 12])
    @patch("start_stage.subprocess.run")
    def test_no_calls_for_non_gate_stages(self, mock_run, stage, tmp_wrk):
        _auto_open_html_for_human_gates("WRK-9999", stage, str(tmp_wrk))
        mock_run.assert_not_called()


class TestOpensBothHtmlForStage5:
    """Stage 5 should call the browser script twice with plan_draft."""

    @patch("start_stage.subprocess.run")
    def test_opens_both_html_for_stage_5(self, mock_run, tmp_wrk):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        _auto_open_html_for_human_gates("WRK-9999", 5, str(tmp_wrk))
        assert mock_run.call_count == 2
        # Verify stage arg is plan_draft
        for call in mock_run.call_args_list:
            args = call[0][0]
            stage_idx = args.index("--stage") + 1
            assert args[stage_idx] == "plan_draft"


class TestStage7MapsToPlanFinal:
    """Stage 7 should map to plan_final."""

    @patch("start_stage.subprocess.run")
    def test_stage_7_maps_to_plan_final(self, mock_run, tmp_wrk):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        _auto_open_html_for_human_gates("WRK-9999", 7, str(tmp_wrk))
        assert mock_run.call_count == 2
        for call in mock_run.call_args_list:
            args = call[0][0]
            stage_idx = args.index("--stage") + 1
            assert args[stage_idx] == "plan_final"


class TestStage17MapsToCloseReview:
    """Stage 17 should map to close_review."""

    @patch("start_stage.subprocess.run")
    def test_stage_17_maps_to_close_review(self, mock_run, tmp_wrk):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        _auto_open_html_for_human_gates("WRK-9999", 17, str(tmp_wrk))
        assert mock_run.call_count == 2
        for call in mock_run.call_args_list:
            args = call[0][0]
            stage_idx = args.index("--stage") + 1
            assert args[stage_idx] == "close_review"


class TestSkipsWhenAlreadyOpened:
    """Pre-populated evidence should prevent duplicate opens."""

    @patch("start_stage.subprocess.run")
    def test_skips_when_already_opened(self, mock_run, tmp_wrk):
        _make_evidence(tmp_wrk, ["plan_draft"])
        _auto_open_html_for_human_gates("WRK-9999", 5, str(tmp_wrk))
        mock_run.assert_not_called()


class TestSkipsMissingHtmlGracefully:
    """Missing HTML files should warn but not crash."""

    @patch("start_stage.subprocess.run")
    def test_skips_missing_html_gracefully(self, mock_run, tmp_wrk):
        # Remove HTML files
        assets = tmp_wrk / ".claude" / "work-queue" / "assets" / "WRK-9999"
        (assets / "WRK-9999-lifecycle.html").unlink()
        (assets / "WRK-9999-plan.html").unlink()
        # Should not crash
        _auto_open_html_for_human_gates("WRK-9999", 5, str(tmp_wrk))
        mock_run.assert_not_called()
