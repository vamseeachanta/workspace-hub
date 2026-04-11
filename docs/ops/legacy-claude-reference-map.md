# Legacy Claude Reference Map

Purpose: map high-frequency historical Claude session paths to the current workspace-hub workflow so future agents do not chase deleted files.

## Canonical current model

```text
GitHub Issue -> GSD plan in .planning/ -> implementation -> cross-review -> close issue
```

Primary anchors:
- `AGENTS.md`
- `docs/work-queue-workflow.md`
- `docs/governance/SESSION-GOVERNANCE.md`
- `scripts/workflow/governance-checkpoints.yaml`
- `scripts/review/cross-review.sh`
- `scripts/refresh-agent-work-queue.py`
- `notes/agent-work-queue.md`

## High-signal legacy path redirects

### 1. Legacy work-queue gate / transition scripts

Historical paths:
- `scripts/work-queue/verify-gate-evidence.py`
- `scripts/work-queue/generate-html-review.py`
- `scripts/work-queue/start_stage.py`
- `scripts/work-queue/exit_stage.py`
- `scripts/work-queue/verify_checklist.py`
- `scripts/work-queue/stage_exit_checks.py`
- `.claude/hooks/enforce-active-stage.sh`

Use now:
- `docs/governance/SESSION-GOVERNANCE.md`
- `docs/governance/TRUST-ARCHITECTURE.md`
- `scripts/workflow/governance-checkpoints.yaml`
- `.claude/hooks/plan-approval-gate.sh`
- `.claude/hooks/session-governor-check.sh`
- `scripts/review/cross-review.sh`

Interpretation:
- These old files were removed during workflow migration.
- `generate-html-review.py` was part of the old review/gate surface; use `scripts/review/cross-review.sh` plus current review evidence instead of restoring the generator.
- Do not try to recreate them as active executables unless a specific live integration still requires them.

### 2. Legacy work-queue lifecycle scripts

Historical paths:
- `scripts/work-queue/close-item.sh`
- `scripts/work-queue/whats-next.sh`
- `scripts/work-queue/archive-item.sh`
- `scripts/work-queue/claim-item.sh`
- `.claude/work-queue/scripts/generate-index.py`

Use now:
- `scripts/refresh-agent-work-queue.py`
- `scripts/refresh-agent-work-queue.sh`
- `notes/agent-work-queue.md`
- `.planning/`
- GitHub issue state and comments

Interpretation:
- The repo no longer treats local queue scripts as canonical work orchestration.
- Prefer issue updates plus `.planning/` evidence.

### 3. Stage YAML contracts

Historical paths:
- `scripts/work-queue/stages/stage-01-capture.yaml`
- `scripts/work-queue/stages/stage-05-user-review-plan-draft.yaml`
- `scripts/work-queue/stages/stage-07-user-review-plan-final.yaml`
- `scripts/work-queue/stages/stage-10-work-execution.yaml`

Use now:
- `.planning/templates/stage-evidence-template.yaml`
- `.planning/templates/stage5-evidence-contract.yaml`
- `.planning/templates/user-review-capture.yaml`
- `.planning/templates/user-review-plan-draft-template.yaml`
- `.planning/templates/user-review-publish-template.yaml`
- `scripts/workflow/governance-checkpoints.yaml`

Interpretation:
- Historical staged contracts were removed; modern workflow evidence lives in `.planning/templates/` plus governance checkpoints.

### 4. Removed work-queue skills

Historical paths:
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `.claude/skills/coordination/workspace/work-queue/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`

Use now:
- `AGENTS.md`
- `.claude/commands/gsd/*`
- `.gemini/get-shit-done/workflows/*`
- `docs/work-queue-workflow.md`

Interpretation:
- The old skill tree was replaced by GSD-oriented command/workflow surfaces.

### 5. Removed provider wrapper tree

Historical paths:
- `scripts/agents/session.sh`
- `scripts/agents/work.sh`
- `scripts/agents/plan.sh`
- `scripts/agents/execute.sh`
- `scripts/agents/review.sh`
- `scripts/agents/lib/workflow-guards.sh`
- `scripts/agents/providers/claude.sh`
- `scripts/agents/providers/codex.sh`
- `scripts/agents/providers/gemini.sh`

Use now:
- `AGENTS.md`
- `docs/modules/ai/AGENT_EQUIVALENCE_ARCHITECTURE.md`
- `docs/work-queue-workflow.md`
- `scripts/review/cross-review.sh`
- `scripts/refresh-agent-work-queue.py`
- `scripts/planning/ensemble-plan.sh` (self-contained fallback helpers; no external `scripts/agents/lib/workflow-guards.sh` dependency)

Interpretation:
- Older planning and review sessions may still reference `scripts/agents/*`.
- Those references are stale and should be redirected, not reintroduced blindly.

### 6. Missing session-start skill path

Historical path:
- `.claude/skills/workspace-hub/session-start/SKILL.md`

Use now:
- `AGENTS.md`
- `scripts/session/repo-map-context.py`
- `scripts/session/data-intelligence-context.py`
- `.claude/hooks/session-governor-check.sh`

Interpretation:
- Session startup behavior is now split across project policy, helper scripts, and hooks rather than one canonical legacy skill file.

## Anti-patterns

Do not:
- treat deleted `scripts/work-queue/*` files as current workflow requirements
- restore stage executables just because they appear in historical session logs
- use `scripts/work-queue/close-item.sh` as a live completion path

Do:
- map legacy references to current docs, hooks, and `.planning/` artifacts
- treat historical log reads as migration signals, not as proof that the old files should return
- update agent-facing docs when legacy references reappear
