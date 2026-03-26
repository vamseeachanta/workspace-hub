# WRK-1083 Stage 4 Plan — Plan-Mode Integration

## Context
All implementation commits are already done from a prior session:
- `c4abb974` feat(WRK-1083): add workspace-hub/plan-mode skill
- `27f87f82` feat(WRK-1083): add plan_mode: required to stages 4,6,10,13
- `91560bf2` feat(WRK-1083): wire plan-mode skill into workflow + stage micro-skills

Stage 4 (Plan Draft) was never formally exited, so the checkpoint remains at Stage 4.

## What Was Implemented (All ACs met)

| AC | Status | Evidence |
|----|--------|---------|
| Stages enumerated with rationale | ✅ | plan-mode/SKILL.md lines 23-29 |
| planning skill created/wired | ✅ | .claude/skills/workspace-hub/plan-mode/SKILL.md |
| work-queue-workflow references skill | ✅ | SKILL.md §Plan-Mode Gates (lines 155-167) |
| ≥1 stage contract has plan_mode: required | ✅ | stages 4, 6, 10, 13 all have it |
| writing-plans reviewed + wired in | ✅ | plan-mode/SKILL.md references superpowers/writing-plans |

## Stage 4 Completion Steps (post-plan-mode exit)

1. Write `specs/wrk/WRK-1083/plan.md` (formal plan artifact)
2. Regenerate lifecycle HTML: `generate-html-review.py WRK-1083 --lifecycle`
3. Run `exit_stage.py WRK-1083 4`
4. Proceed to Stage 5 (user review hard gate)

## Stage 5 Steps
- Open lifecycle HTML in browser + push
- Walk ACs with user section-by-section
- Write `evidence/user-review-plan-draft.yaml`
- Wait for explicit user approval
