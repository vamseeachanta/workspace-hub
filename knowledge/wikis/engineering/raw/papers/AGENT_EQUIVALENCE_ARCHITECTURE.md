# Agent Equivalence Architecture

Status: legacy architecture note with current-path redirects.

## Goal
Provide workflow-equivalent behavior across Claude Code, Codex CLI, Gemini CLI, and Hermes while using the current workspace-hub operating model rather than deleted `scripts/agents/*` wrappers.

## Session Rule
The provider where the session starts is the orchestrator. Other providers are subagents for that session.

- Orchestrator: owns planning, approval gates, and final integration.
- Subagents: execute delegated work or reviews; they do not redefine canonical workflow state.

## Current source of truth
- Canonical intake/tracking: GitHub issues
- Canonical planning artifacts: `.planning/`
- Active workflow policy: `AGENTS.md`
- Legacy compatibility note: `docs/work-queue-workflow.md`
- Legacy path redirect map: `docs/ops/legacy-claude-reference-map.md`
- Cross-review entrypoint: `scripts/review/cross-review.sh`
- Provider session exports/audit: `logs/orchestrator/README.md`

## Important correction
The old `scripts/agents/*` wrapper tree referenced by older notes is not present in the current checkout.
Do not build new automation against these deleted paths:
- `scripts/agents/session.sh`
- `scripts/agents/work.sh`
- `scripts/agents/plan.sh`
- `scripts/agents/execute.sh`
- `scripts/agents/review.sh`
- `scripts/agents/providers/*.sh`

If a historical session or stale prompt mentions them, treat that as a migration signal and map it to current workflow surfaces instead.

## Current equivalents
- Session startup / policy loading:
  - `AGENTS.md`
  - `.claude/hooks/session-governor-check.sh`
  - `scripts/session/*`
- Planning gate:
  - GitHub issue -> approved `.planning/` artifact
  - `docs/plans/README.md`
  - `docs/standards/HARD-STOP-POLICY.md`
- Implementation gate:
  - TDD + repo-local tests
  - issue state + `.planning/` evidence
- Review gate:
  - `scripts/review/cross-review.sh`
  - `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- Legacy work-queue refresh/reporting:
  - `scripts/refresh-agent-work-queue.py`
  - `scripts/refresh-agent-work-queue.sh`

## Quick start (current model)
```bash
# 1. Read policy + issue/plan requirements
sed -n '1,220p' AGENTS.md
sed -n '1,220p' docs/work-queue-workflow.md

# 2. Work from the approved GitHub issue / .planning artifact
# 3. Run implementation + tests
# 4. Run cross-review
bash scripts/review/cross-review.sh

# 5. Refresh compatibility queue notes if needed
bash scripts/refresh-agent-work-queue.sh
```
