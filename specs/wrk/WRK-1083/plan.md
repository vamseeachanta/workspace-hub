# WRK-1083 Plan: Plan-Mode Integration for Work-Queue-Workflow Stages

## Mission

Identify which WRK lifecycle stages benefit from `EnterPlanMode`, define activation
contracts, and add a `plan-mode` skill that automates deliberative-stage protection.

## Approach

Route B (medium complexity). All implementation committed in a prior session.

### AC Coverage

| AC | Implementation | Evidence |
|----|----------------|---------|
| Stages enumerated with rationale | `plan-mode/SKILL.md` lines 23-29 (table) | ✅ |
| Planning skill created/wired | `.claude/skills/workspace-hub/plan-mode/SKILL.md` | ✅ |
| `work-queue-workflow` references skill | SKILL.md §Plan-Mode Gates (lines 155-167) | ✅ |
| ≥1 stage contract has `plan_mode: required` | `stage-04-plan-draft.yaml` line 19 (+ stages 6, 10, 13) | ✅ |
| `writing-plans` reviewed + wired in | `plan-mode/SKILL.md` references `superpowers/writing-plans` | ✅ |

### Stages Annotated

| Stage | Name | Reason for Plan Mode |
|-------|------|----------------------|
| 4 | Plan Draft | Think through plan structure before writing lifecycle HTML |
| 6 | Cross-Review | Synthesize 3-provider findings before recording verdict |
| 10 | Work Execution | TDD discipline — plan test strategy before code |
| 13 | Agent Cross-Review | Structured implementation quality analysis before verdict |

### Files Changed

- `NEW` `.claude/skills/workspace-hub/plan-mode/SKILL.md` — plan-mode activation skill
- `MOD` `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md` — §Plan-Mode Gates added
- `MOD` `scripts/work-queue/stages/stage-04-plan-draft.yaml` — `plan_mode: required`
- `MOD` `scripts/work-queue/stages/stage-06-cross-review.yaml` — `plan_mode: required`
- `MOD` `scripts/work-queue/stages/stage-10-work-execution.yaml` — `plan_mode: required`
- `MOD` `scripts/work-queue/stages/stage-13-agent-cross-review.yaml` — `plan_mode: required`

## Tests/Evals

No runnable tests needed (skill/YAML changes only). Verification via gate evidence checks:



| # | Check | Method | Expected |
|---|-------|--------|---------|
| T1 | `plan-mode/SKILL.md` exists and lists 4 stages | file read | All 4 stages in table |
| T2 | `stage-04-plan-draft.yaml` has `plan_mode: required` | grep | Match found |
| T3 | `work-queue-workflow/SKILL.md` has Plan-Mode Gates section | grep | Section present |
| T4 | `stage-06-cross-review.yaml` has `plan_mode: required` | grep | Match found |
| T5 | Plan artifact `specs/wrk/WRK-1083/plan.md` exists | file read | Present |

## Risks / Out-of-Scope

- Does not add programmatic enforcement (hooks); that is a future follow-on.
- `superpowers/writing-plans` was reviewed and judged adequate for the writing phase;
  the new `plan-mode` skill handles *entry* logic only.
