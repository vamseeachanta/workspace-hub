"""Tests for WRK-1161: suppress non-actionable CLI stderr noise."""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"

# ── AC1: exit_stage.py D-item warning suppressed when no D-items ─────────


def test_exit_stage_no_warn_when_import_fails(tmp_path, capsys):
    """D-item ImportError should not print to stderr (suppressed as debug)."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import exit_stage

        # Simulate import failure by patching the import inside
        with patch.dict(sys.modules, {"stage_dispatch": None}):
            # The function should silently return, no stderr
            exit_stage._deterministic_stage_check(1, str(tmp_path), str(REPO_ROOT))
        captured = capsys.readouterr()
        assert "WARN" not in captured.err, (
            "D-item ImportError should not print WARN to stderr"
        )
    finally:
        sys.path.remove(str(SCRIPTS_DIR))


# ── AC2: stage_dispatch.py severity prefixes ─────────────────────────────


def test_stage_dispatch_warn_has_severity_prefix():
    """D-ITEM WARN messages should use [WARN] prefix."""
    content = (SCRIPTS_DIR / "stage_dispatch.py").read_text()
    assert "[WARN]" in content, "stage_dispatch.py should use [WARN] prefix"
    assert "D-ITEM WARN:" not in content, (
        "bare 'D-ITEM WARN:' should be replaced with severity-prefixed version"
    )


def test_stage_dispatch_blocked_has_severity_prefix():
    """D-ITEM BLOCKED messages should use [ERROR] prefix."""
    content = (SCRIPTS_DIR / "stage_dispatch.py").read_text()
    assert "[ERROR]" in content, "stage_dispatch.py should use [ERROR] prefix"
    assert "D-ITEM BLOCKED:" not in content, (
        "bare 'D-ITEM BLOCKED:' should be replaced with severity-prefixed version"
    )


# ── AC3: archive-item.sh logs errors to file, not /dev/null ──────────────


def test_archive_item_no_devnull_on_html():
    """archive-item.sh should not suppress HTML generation errors to /dev/null."""
    content = (REPO_ROOT / "scripts" / "work-queue" / "archive-item.sh").read_text()
    # The generate-html-review.py line should not have 2>/dev/null
    for line in content.splitlines():
        if "generate-html-review.py" in line:
            assert "2>/dev/null" not in line, (
                "HTML generation errors should not be suppressed to /dev/null"
            )


def test_archive_item_logs_html_errors_to_file():
    """archive-item.sh should redirect HTML generation stderr to a log file."""
    content = (REPO_ROOT / "scripts" / "work-queue" / "archive-item.sh").read_text()
    for line in content.splitlines():
        if "generate-html-review.py" in line:
            assert "2>>" in line or "2>" in line, (
                "HTML generation stderr should be redirected to a log file"
            )
            break
    else:
        pytest.fail("generate-html-review.py line not found in archive-item.sh")


# ── AC4: claim-item.sh quota warning to stderr ───────────────────────────


def test_claim_item_quota_warning_to_stderr():
    """Quota file missing warning should go to stderr, not stdout."""
    content = (REPO_ROOT / "scripts" / "work-queue" / "claim-item.sh").read_text()
    for line in content.splitlines():
        if "Quota file missing" in line:
            assert ">&2" in line, (
                "Quota warning should redirect to stderr with >&2"
            )
            break
    else:
        pytest.fail("'Quota file missing' line not found in claim-item.sh")
