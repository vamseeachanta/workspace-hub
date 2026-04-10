"""Smoke tests for cross-review-policy coordination skill."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT
    / ".claude/skills/coordination/cross-review-policy/SKILL.md"
)


def test_skill_file_exists():
    assert SKILL_PATH.exists(), f"Missing: {SKILL_PATH.relative_to(REPO_ROOT)}"


def test_body_contains_routing_policy():
    body = SKILL_PATH.read_text()
    assert "AI_REVIEW_ROUTING_POLICY" in body, (
        "Body must reference AI_REVIEW_ROUTING_POLICY"
    )
