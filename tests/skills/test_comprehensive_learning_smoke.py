"""Smoke tests for comprehensive-learning-wrapper skill and cron script."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_PATH = (
    REPO_ROOT
    / ".claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md"
)
CRON_SCRIPT = REPO_ROOT / "scripts/cron/comprehensive-learning-nightly.sh"


def test_wrapper_skill_exists():
    assert WRAPPER_PATH.exists(), (
        f"Missing: {WRAPPER_PATH.relative_to(REPO_ROOT)}"
    )


def test_cron_script_exists():
    assert CRON_SCRIPT.exists(), (
        f"Missing: {CRON_SCRIPT.relative_to(REPO_ROOT)}"
    )
