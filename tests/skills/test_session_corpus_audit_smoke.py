"""Smoke tests for session-corpus-audit coordination skill."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT
    / ".claude/skills/coordination/session-corpus-audit/SKILL.md"
)


def test_skill_file_exists():
    assert SKILL_PATH.exists(), f"Missing: {SKILL_PATH.relative_to(REPO_ROOT)}"


def test_has_frontmatter():
    text = SKILL_PATH.read_text()
    assert text.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert text.count("---") >= 2, "Frontmatter must have opening and closing ---"
