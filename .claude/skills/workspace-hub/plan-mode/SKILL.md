---
name: plan-mode
description: >
  Invoke EnterPlanMode at deliberative WRK stages before writing any artifact.
  Prevents premature file writes during analysis and synthesis phases.
version: 1.0.0
updated: 2026-03-09
category: workspace-hub
triggers:
  - Stage 4 plan draft
  - Stage 6 cross-review
  - Stage 10 work execution
  - Stage 13 agent cross-review
related_skills:
  - workspace-hub/work-queue-workflow
  - superpowers/writing-plans
tags: []
---
# Plan-Mode Gates

## When to Enter Plan Mode

Call `EnterPlanMode` at the START of these stages, before touching any file:

| Stage | Name | Rationale |
|-------|------|-----------|
| Stage 4 | Plan Draft | Think through plan structure before writing lifecycle HTML |
| Stage 6 | Cross-Review | Synthesize 3-provider findings; premature writes corrupt the verdict |
| Stage 10 | Work Execution | Plan test + file strategy before implementation commits |
| Stage 13 | Agent Cross-Review | Structured analysis of implementation quality before recording verdict |

## Invocation Pattern

```
1. EnterPlanMode          ← no file writes until plan is complete
2. Think through approach, risks, and artifact layout
3. ExitPlanMode           ← only now write artifacts
4. Write stage evidence / lifecycle HTML via Write tool
```

## Why This Matters

Plan mode is a cognitive gate, not a process formality:
- Cross-review stages (6, 13): entering plan mode forces synthesis of all provider
  inputs before any verdict is written; prevents anchoring to the first finding seen.
- Work execution (10): forces test-strategy decisions before code is written,
  ensuring TDD discipline (red → green → refactor).
- Plan draft (4): prevents partial plans from being committed as HTML before
  structure is complete.

## Plan Format Reference

For plan artifact structure (tasks, pseudocode, 2-5 min step granularity),
see `superpowers/writing-plans`.

## Enforcement

`plan_mode: required` is declared in each stage's contract YAML
(`scripts/work-queue/stages/stage-{04,06,10,13}-*.yaml`).
Enforcement is skill-level discipline; hook automation is tracked in WRK-305.
