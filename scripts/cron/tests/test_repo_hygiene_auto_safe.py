"""Tests for the scheduled report-first repo hygiene wrapper."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "repo-hygiene-auto-safe.sh"


def test_wrapper_runs_report_before_apply_and_does_not_apply_caches() -> None:
    text = SCRIPT.read_text()

    report_index = text.index("run_hygiene report")
    apply_index = text.index("run_hygiene apply")
    assert report_index < apply_index
    assert '--apply "${EXTRA_ARGS[@]}"' in text
    assert "EXTRA_ARGS" in text
    assert "--caches" not in text


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
