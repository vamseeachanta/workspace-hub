# AC Test Matrix — WRK-1014

| # | Test | Type | Command | Result |
|---|------|------|---------|--------|
| 1 | `EnterPlanMode`/`ExitPlanMode` in SKILL.md tools array | happy | `grep 'EnterPlanMode' .claude/skills/coordination/workspace/work-queue/SKILL.md` | **PASS** |
| 2 | Stage Contracts table has 4a and 4b rows | happy | `grep '4a\|4b' .claude/skills/coordination/workspace/work-queue/SKILL.md` | **PASS** |
| 3 | Mermaid flowchart has `4a: Plan Mode Ideation` node | happy | `grep '4a: Plan Mode Ideation' .claude/work-queue/process.md` | **PASS** |
| 4 | process.md Stage 4 has explicit coverage instruction | happy | `grep 'explicit' .claude/work-queue/process.md` | **PASS** |
| 5 | process.md Stage 4b has self-verification pass | happy | `grep 'self-verification' .claude/work-queue/process.md` | **PASS** |
| 6 | work-queue-workflow/SKILL.md step 3 references 4a/4b | happy | `grep '4a\|4b' .claude/skills/workspace-hub/work-queue-workflow/SKILL.md` | **PASS** |
| 7 | SKILL.md line count ≤ 250 | edge | `wc -l .claude/skills/coordination/workspace/work-queue/SKILL.md` → 250 | **PASS** |
| 8 | Legal scan passes | happy | `bash scripts/legal/legal-sanity-scan.sh` | **PASS** |

**Summary: 8 PASS, 0 FAIL, 0 SKIP**
