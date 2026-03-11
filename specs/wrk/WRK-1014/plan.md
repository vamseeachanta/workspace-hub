# Plan: WRK-1014 — Add Stage 4a Plan Mode Ideation to WRK Lifecycle

## Mission

Insert a `EnterPlanMode` / `ExitPlanMode` sub-stage (4a) before existing Stage 4b
artifact creation so the orchestrator drafts the full plan scope as text before touching
any files — higher quality first drafts, less rework.

## What / Why / Context

Stage 4 currently jumps straight to writing `specs/wrk/WRK-NNN/plan.md` and generating
HTML. Iterating on a wrong approach requires regenerating artifacts repeatedly.
Pattern surfaced during WRK-1005: user asked whether EnterPlanMode should gate plan draft.
This WRK implements that answer as a documented lifecycle sub-stage.

Benchmark evidence (Matt Maher planning benchmark, 2026-03-10): explicit coverage
instructions inside plan mode produce ~15-point higher coverage vs implicit plan mode.
Incorporated into the 4a/4b guidance as a result.

## Files to Modify

1. `.claude/skills/coordination/workspace/work-queue/SKILL.md`
   - Add `EnterPlanMode`, `ExitPlanMode` to tools frontmatter array
   - Split Stage 4 row in Canonical Lifecycle list to show 4a sub-stage
   - Split Stage 4 row in Stage Contracts table into 4a and 4b rows

2. `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
   - Update Start-to-Finish Chain step 3 to describe 4a/4b split and explicit
     coverage instruction requirement

3. `.claude/work-queue/process.md`
   - Replace `D[Plan Draft]` node with `D[4a: Plan Mode Ideation] --> D2[4b: Plan Artifact Write]`
   - Add 4a/4b prose paragraphs to Stage 4 contract section including:
     - Explicit coverage instruction requirement
     - Self-verification pass at 4b before writing artifact

## Tests / Evals

| Test | Type | Expected |
|------|------|----------|
| SKILL.md contains `EnterPlanMode` in tools array | happy | grep finds it |
| SKILL.md Stage Contracts table has 4a and 4b rows | happy | both rows present |
| process.md Mermaid has `4a: Plan Mode Ideation` node | happy | node present |
| process.md Stage 4 section has explicit coverage instruction warning | happy | text present |
| work-queue-workflow/SKILL.md step 3 references 4a/4b | happy | text present |
| SKILL.md line count ≤ 250 | edge | wc -l ≤ 250 |

## Risks / Out of Scope

- No stage numbers renamed (4a/4b are sub-stages only)
- No stage-NN-*.yaml contract files changed
- No code changes — doc/YAML only
- Stage 4a is non-blocking (no exit artifact required)
