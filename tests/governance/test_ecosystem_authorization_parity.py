"""Ensure native skill mirrors and active pipeline routes follow task authority."""
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
MIRRORS = [
    "coordination/issue-planning-mode/SKILL.md",
    "coordination/gh-work-planning/SKILL.md",
    "github/github-issue-lifecycle-operations/SKILL.md",
    "github/github-issue-lifecycle-operations/references/gh-work-execution.md",
    "github/github-issue-lifecycle-operations/references/gh-work-planning.md",
    "coordination/continuous-planning-pipeline/SKILL.md",
    "github/github-issue-lifecycle-operations/references/continuous-planning-pipeline.md",
    "coordination/hermes-workflow-audit/SKILL.md",
    "coordination/subagent-sandbox-limitations/SKILL.md",
]
ACTIVE = MIRRORS[-4:] + [
    "coordination/subagent-sandbox-limitations/references/gated-issue-batch-parallel-recon.md",
    "coordination/llm-wiki-roadmap-integration/references/weekly-cadence-issue-wave.md",
    "ai/inventory-readiness-provider-dispatch/SKILL.md",
    "ai/provider-session-quota-operations/references/workstation-aware-provider-orchestration.md",
    "ai/provider-session-quota-operations/references/provider-utilization-scorecard.md",
    "workspace-hub/plan-gated-issue-execution-wave/SKILL.md",
    "coordination/plan-gated-overnight-queue-partition/SKILL.md",
    "coordination/overnight-worktree-agent-waves/references/plan-gated-overnight-queue-partition.md",
    "workspace-hub-learned/user-approved-plan-state-sync/SKILL.md",
    "research/llm-wiki-cadence-governance/SKILL.md",
]
STALE = [
    "Issue → Plan → USER APPROVES → Implement",
    "Can agent implement? requires `status:plan-approved`",
    "issue has `status:plan-approved`",
    "local approval marker exists and is committed",
    "missing plan approval",
    "plan approval is missing",
    "keep `status:plan-review` siblings out of execution until explicit user approval",
    "user approval -> status:plan-approved -> implementation",
    "Do not launch implementation until `status:plan-approved` is present",
]


@pytest.mark.parametrize("relative", MIRRORS)
def test_native_primary_skills_match_canonical_authority(relative):
    assert (ROOT / ".agents/skills" / relative).read_bytes() == (ROOT / ".claude/skills" / relative).read_bytes()


@pytest.mark.parametrize("relative", ACTIVE)
def test_active_routes_do_not_require_separate_plan_approval(relative):
    text = (ROOT / ".claude/skills" / relative).read_text(encoding="utf-8")
    assert "task" in text.lower() and "authority" in text.lower()
    for requirement in STALE:
        assert requirement not in text


def test_canonical_lifecycle_retains_completeness_and_action_boundaries():
    text = (ROOT / ".agents/skills/github/github-issue-lifecycle-operations/SKILL.md").read_text(encoding="utf-8")
    planning = (ROOT / ".agents/skills/coordination/issue-planning-mode/SKILL.md").read_text(encoding="utf-8")
    assert "completeness" in planning.lower()
    assert "consequential" in text.lower()
    assert "TDD" in text and "review" in text.lower()


@pytest.mark.parametrize("relative", MIRRORS[:3])
def test_native_primary_referenced_resources_exist_and_match(relative):
    source = ROOT / ".claude/skills" / relative
    native = ROOT / ".agents/skills" / relative
    references = set(re.findall(r"`([^`\n]*references/[A-Za-z0-9_-]+\.md)`", source.read_text(encoding="utf-8")))
    assert references
    for name in references:
        canonical = source.parent / name
        target = native.parent / name
        assert canonical.is_file(), str(canonical)
        assert target.is_file(), str(target)
        assert canonical.read_bytes() == target.read_bytes(), name


CRITICAL_ROUTES = [
    'ai/agent-usage-optimizer/SKILL.md',
    'ai/agent-usage-optimizer/references/kanban-approval-control-plane.md',
    'ai/durable-provider-throughput-dispatch/SKILL.md',
    'ai/inventory-readiness-provider-dispatch/SKILL.md',
    'ai/provider-session-quota-operations/references/inventory-readiness-provider-dispatch.md',
    'ai/provider-session-quota-operations/references/provider-utilization-scorecard.md',
    'ai/provider-session-quota-operations/references/workstation-aware-provider-orchestration.md',
    'ai/provider-utilization-scorecard/SKILL.md',
    'autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md',
    'autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-stdin-close.md',
    'autonomous-ai-agents/codex-background-burn-orchestration/SKILL.md',
    'autonomous-ai-agents/codex-background-stdin-close/SKILL.md',
    'coordination/agent-label-routing/references/layered-kanban-flow-routing.md',
    'coordination/closed-issue-plan-refile-loop/SKILL.md',
    'coordination/continuous-planning-pipeline/SKILL.md',
    'coordination/engineering-issue-workflow/references/engineering-calculation-plan-hardening.md',
    'coordination/gh-work-planning-checklist/SKILL.md',
    'coordination/gh-work-planning-checklist/references/interactive-review-thread-mode.md',
    'coordination/github-label-approval-reconciliation/SKILL.md',
    'coordination/hermes-workflow-audit/SKILL.md',
    'coordination/issue-planning-mode/SKILL.md',
    'coordination/llm-wiki-roadmap-integration/references/weekly-cadence-issue-wave.md',
    'coordination/overnight-worktree-agent-waves/SKILL.md',
    'coordination/overnight-worktree-agent-waves/references/plan-gated-overnight-queue-partition.md',
    'coordination/parallel-plan-drafting-worktrees/SKILL.md',
    'coordination/plan-exit-governance-drift-handoff/SKILL.md',
    'coordination/plan-gated-overnight-queue-partition/SKILL.md',
    'coordination/plan-rerun-state-revalidation/SKILL.md',
    'coordination/subagent-sandbox-limitations/SKILL.md',
    'coordination/subagent-sandbox-limitations/references/gated-issue-batch-parallel-recon.md',
    'coordination/workflow-compliance-audit/SKILL.md',
    'development/improve-codebase-architecture/SKILL.md',
    'development/improve-codebase-architecture/references/ecosystem-candidate-issue-expansion.md',
    'devops/hermes-ecosystem-integration/references/sibling-repo-sso-topology.md',
    'devops/hermes-ecosystem-integration/references/sibling-sso-post-landing-followup.md',
    'devops/hermes-local-configuration/references/messaging-platform-routing.md',
    'devops/kanban-orchestrator/SKILL.md',
    'devops/kanban-orchestrator/references/github-label-derived-portfolio-board.md',
    'engineering/engineering-domain-reconnaissance/references/external-drive-ingest-planning.md',
    'github/github-issue-lifecycle-operations/SKILL.md',
    'github/github-issue-lifecycle-operations/references/closed-issue-plan-refile-loop.md',
    'github/github-issue-lifecycle-operations/references/continuous-planning-pipeline.md',
    'github/github-issue-lifecycle-operations/references/parallel-approved-issue-worktrees.md',
    'github/github-issue-lifecycle-operations/references/parallel-plan-drafting-worktrees.md',
    'github/github-issues/references/closed-issue-revision-thread.md',
    'github/github-issues/references/data-governance-usage-level-matrix.md',
    'github/github-issues/references/issue-tree-exit-closeout.md',
    'github/github-issues/references/layered-architecture-review-issue-tree.md',
    'github/github-issues/references/scheduler-routing-issue-tree.md',
    'operations/telegram-hermes-bot/references/control-surface-issue-tree.md',
    'operations/telegram-hermes-bot/references/multi-machine-dispatch.md',
    'research/llm-wiki-cadence-governance/SKILL.md',
    'research/llm-wiki-weekly-freshness/SKILL.md',
    'research/llm-wiki/SKILL.md',
    'research/llm-wiki/references/yaw-moment-raw-reference-ingestion.md',
    'software-development/gh-work-execution-checklist/SKILL.md',
    'software-development/overnight-parallel-agent-prompts/SKILL.md',
    'software-development/parallel-approved-issue-worktrees/SKILL.md',
    'software-development/plan-review-adversarial-hardening/SKILL.md',
    'software-development/plan-review-adversarial-hardening/references/plan-exit-governance-drift-handoff.md',
    'software-development/plan-review-adversarial-hardening/references/plan-rerun-state-revalidation.md',
    'software-development/plan-review-adversarial-hardening/references/plan-review-rerun-cli-drift-and-git-contention.md',
    'software-development/plan-review-adversarial-hardening/references/provider-unavailable-plan-review-holding-pattern.md',
    'software-development/plan-review-adversarial-hardening/references/ten-agent-pre-plan-review-wave.md',
    'software-development/plan-review-adversarial-hardening/references/user-approved-plan-state-sync.md',
    'workspace-hub-learned/closure-first-overnight-batch/SKILL.md',
    'workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/SKILL.md',
    'workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/references/weekly-cadence-code-utility-roadmap.md',
    'workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/references/weekly-cadence-plan-review-hardening.md',
    'workspace-hub-learned/user-approved-plan-state-sync/SKILL.md',
    'workspace-hub/domain-knowledge-sweep/SKILL.md',
    'workspace-hub/learned/plan-gated-issue-implementation/SKILL.md',
    'workspace-hub/plan-gated-issue-execution-wave/SKILL.md',
    'workspace-hub/repo-mission-portfolio-audit/SKILL.md',
    'workspace-hub/repo-structure/references/phase1-contract-checker-pattern.md',
    'workspace-hub/workspace-knowledge-doc-contracts/SKILL.md',
    'workspace-hub/workspace-knowledge-doc-contracts/references/repo-mission-portfolio-audit.md',
]


@pytest.mark.parametrize("relative", CRITICAL_ROUTES)
def test_all_owned_canonical_routes_reject_label_only_execution_gates(relative):
    text = (ROOT / ".claude/skills" / relative).read_text(encoding="utf-8")
    for requirement in [
        "`status:plan-review` or draft issues: planning/review hardening only",
        "Wait for approval -> Execute only after approval",
        "hard gates: verify issue open + `status:plan-approved`",
        "confirm each issue is `status:plan-approved`",
        "confirm explicit plan approval (`status:plan-approved` or a local approval marker)",
        "create/commit the local `.planning/plan-approved/<issue>.md` marker before launching",
        "marker committed in that worktree before starting",
        "approval marker path, label transition",
    ]:
        assert requirement not in text
    native = ROOT / ".agents/skills" / relative
    if native.exists():
        assert native.read_bytes() == (ROOT / ".claude/skills" / relative).read_bytes()


@pytest.mark.parametrize("relative,obsolete", [
    ("scripts/enforcement/enforcement-env.sh", "1 = block commits without plan approval"),
    ("scripts/enforcement/upgrade-enforcement.sh", "STRICT (will block commits without plan approval)"),
    ("scripts/workflow/completeness_gate_runner.py", "only enforces issues that reached implementation (`status:plan-approved`)"),
])
def test_runtime_descriptions_do_not_reintroduce_retired_authorization(relative, obsolete):
    assert obsolete not in (ROOT / relative).read_text(encoding="utf-8")
