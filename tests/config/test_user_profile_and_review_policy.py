"""Consistency checks for shared user profile and review policy."""
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
USER_PROFILE = REPO_ROOT / "config" / "user-profile.yaml"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
REVIEW_POLICY = REPO_ROOT / "docs" / "standards" / "AI_REVIEW_ROUTING_POLICY.md"


def test_user_profile_exists_with_review_agents():
    with open(USER_PROFILE) as handle:
        data = yaml.safe_load(handle)
    review_policy = data["workflow_preferences"]["review_policy"]
    assert review_policy["plan_review_agents"] == ["Claude", "Codex", "Gemini"]
    assert review_policy["artifact_review_agents"] == ["Claude", "Codex", "Gemini"]


def test_agents_and_review_policy_reference_all_three_reviewers():
    agents_text = AGENTS_MD.read_text()
    policy_text = REVIEW_POLICY.read_text()
    assert "Claude, Codex, and Gemini" in agents_text
    assert "Claude + Codex + Gemini all review" in policy_text
