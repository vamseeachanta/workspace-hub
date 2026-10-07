"""Active dispatch guidance must not reintroduce retired implementation gates."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "software-development/gh-work-execution",
    "ai/provider-utilization-scorecard",
    "coordination/workstation-aware-provider-orchestration",
    "autonomous-ai-agents/claude-code",
    "github/github-issues",
    "workspace-hub/external-drive-ingest-planning",
    "workspace-hub-learned/ten-agent-pre-plan-review-wave",
    "workspace-hub-learned/plan-review-rerun-cli-drift-and-git-contention",
]
SURFACES = [f"{root}/skills/{skill}/SKILL.md"
            for root in (".claude", ".agents") for skill in SKILLS
            if (ROOT / root / "skills" / skill / "SKILL.md").exists()]


@pytest.mark.parametrize("path", SURFACES)
def test_dispatch_guidance_uses_task_authority_without_separate_plan_gate(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    assert "task request or standing authority" in text.lower(), path
    assert "no separate user plan approval" in text.lower(), path
    for obsolete in (
        "Only start execution when the issue is already labeled `status:plan-approved`",
        "Never dispatch implementation from status:plan-review",
        "Launch only plan-approved implementation lanes",
        "implementation remains blocked until explicit user approval",
        "stop at `status:plan-review` until the user approves",
        "still not implementation-ready until explicit user approval",
        "Issue -> Plan -> User approves -> TDD implementation",
        "Use it only after planning is complete and the issue is approved",
    ):
        assert obsolete not in text, (path, obsolete)


@pytest.mark.parametrize("path", SURFACES)
def test_dispatch_scope_keeps_real_decisions_and_consequential_boundaries(path):
    text = (ROOT / path).read_text(encoding="utf-8").lower()
    for boundary in ("planning-only", "domain decisions", "consequential actions", "implementation authority alone does not authorize publication", "reuse it when already provided"):
        assert boundary in text, (path, boundary)


def test_all_provider_contracts_preserve_authorized_completion_posture():
    shared = (ROOT / "config/agents/SHARED_SOUL.md").read_text(encoding="utf-8")
    for phrase in ("ongoing and future chats", "implementation and verification", "draft PR", "specific next checkpoint", "does not authorize unrelated work"):
        assert phrase in shared
    for provider, name in (("claude", "SOUL.runtime.md"), ("codex", "AGENTS.runtime.md"), ("codex", "SOUL.runtime.md"), ("gemini", "SOUL.runtime.md"), ("hermes", "SOUL.runtime.md"), ("agy", "SOUL.runtime.md")):
        runtime = (ROOT / "config/agents" / provider / name).read_text(encoding="utf-8")
        assert shared in runtime
