# WRK-1083 AC Test Matrix

| # | Test | Command | Result |
|---|------|---------|--------|
| T1 | plan-mode skill file exists | `test -f .claude/skills/workspace-hub/plan-mode/SKILL.md` | PASS |
| T2 | stage-04 has plan_mode: required | `grep -q 'plan_mode: required' scripts/work-queue/stages/stage-04-plan-draft.yaml` | PASS |
| T3 | stage-06 has plan_mode: required | `grep -q 'plan_mode: required' scripts/work-queue/stages/stage-06-cross-review.yaml` | PASS |
| T4 | stage-10 has plan_mode: required | `grep -q 'plan_mode: required' scripts/work-queue/stages/stage-10-work-execution.yaml` | PASS |
| T5 | stage-13 has plan_mode: required | `grep -q 'plan_mode: required' scripts/work-queue/stages/stage-13-agent-cross-review.yaml` | PASS |
| T6 | workflow skill references plan-mode gates | `grep -q 'Plan-Mode Gates' .claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | PASS |
| T7 | plan-mode skill lists 4 stages in table | `grep -c '| Stage' .claude/skills/workspace-hub/plan-mode/SKILL.md` → 5 (header+4) | PASS |
| T8 | writing-plans referenced in skill body | `grep -q 'writing-plans' .claude/skills/workspace-hub/plan-mode/SKILL.md` | PASS |
