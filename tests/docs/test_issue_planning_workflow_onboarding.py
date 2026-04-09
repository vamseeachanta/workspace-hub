"""Tests verifying all agents are properly onboarded to the strict issue planning workflow.

Acceptance criteria for #2045:
- Agent onboarding docs explicitly reference the planning workflow
- Planning skill and template exist and are non-empty
- GitHub label constants are documented in onboarding docs
- docs/plans/README.md describes the full status lifecycle
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENTS_PATH = REPO_ROOT / "AGENTS.md"
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
PLANS_README = REPO_ROOT / "docs" / "plans" / "README.md"
PLAN_TEMPLATE = REPO_ROOT / "docs" / "plans" / "_template-issue-plan.md"
PLANNING_SKILL = REPO_ROOT / ".claude" / "skills" / "coordination" / "issue-planning-mode" / "SKILL.md"


# ── AGENTS.md tests ────────────────────────────────────────────────────────────

def test_agents_references_planning_skill():
    text = AGENTS_PATH.read_text()
    assert "issue-planning-mode" in text, (
        "AGENTS.md must reference the issue-planning-mode skill so all agents load it"
    )


def test_agents_mentions_plan_review_label():
    text = AGENTS_PATH.read_text()
    assert "status:plan-review" in text, (
        "AGENTS.md must name the status:plan-review label agents must apply"
    )


def test_agents_mentions_plan_approved_label():
    text = AGENTS_PATH.read_text()
    assert "status:plan-approved" in text, (
        "AGENTS.md must name the status:plan-approved label that gates batch execution"
    )


def test_agents_planning_applies_to_all_issues():
    text = AGENTS_PATH.read_text()
    # phrase must signal ALL issues, not only engineering-critical
    lower = text.lower()
    assert "all issues" in lower, (
        "AGENTS.md must state that the planning workflow applies to ALL issues"
    )


# ── CLAUDE.md tests ────────────────────────────────────────────────────────────

def test_claude_md_references_planning_workflow():
    text = CLAUDE_PATH.read_text()
    assert "issue-planning-mode" in text or "planning workflow" in text.lower(), (
        "CLAUDE.md must reference the planning workflow or issue-planning-mode skill"
    )


def test_claude_md_mentions_plan_review_label():
    text = CLAUDE_PATH.read_text()
    assert "status:plan-review" in text, (
        "CLAUDE.md must name status:plan-review so Claude agents know to apply it"
    )


# ── Skill and template presence ────────────────────────────────────────────────

def test_planning_skill_exists_and_is_non_empty():
    assert PLANNING_SKILL.exists(), "issue-planning-mode SKILL.md must exist"
    text = PLANNING_SKILL.read_text()
    assert len(text) > 500, "Planning skill must contain substantive content (>500 chars)"


def test_plan_template_exists_and_is_non_empty():
    assert PLAN_TEMPLATE.exists(), "_template-issue-plan.md must exist in docs/plans/"
    text = PLAN_TEMPLATE.read_text()
    assert "TDD Test List" in text, "Plan template must include a TDD Test List section"
    assert "Adversarial Review" in text, "Plan template must include an Adversarial Review section"
    assert "status:plan-review" in text or "plan-review" in text, (
        "Plan template must reference the plan-review status"
    )


# ── docs/plans/README.md tests ─────────────────────────────────────────────────

def test_plans_readme_documents_full_status_lifecycle():
    text = PLANS_README.read_text()
    for status in ("draft", "adversarial-reviewed", "plan-review", "plan-approved", "completed"):
        assert status in text, f"docs/plans/README.md must document '{status}' in the status lifecycle"


def test_plans_readme_instructs_batch_agents():
    text = PLANS_README.read_text()
    assert "plan-approved" in text and "batch" in text.lower(), (
        "docs/plans/README.md must state batch agents only act on plan-approved issues"
    )
