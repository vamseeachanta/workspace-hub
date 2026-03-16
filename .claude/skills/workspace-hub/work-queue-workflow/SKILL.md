---
name: work-queue-workflow
description: 'Explicit entrypoint skill for the WRK work-queue lifecycle workflow.
  Points to the canonical work-queue process and gatepass enforcement sequence.

  '
version: 1.8.0
updated: 2026-03-12
category: workspace-hub
triggers:
- work-queue workflow
- wrk workflow
- /work workflow
- lifecycle workflow
related_skills:
- work-queue
- workflow-gatepass
- workflow-html
- session-start
- session-end
capabilities:
- workflow-entrypoint
- lifecycle-routing
- gatepass-handoff
requires:
- .claude/work-queue/process.md
invoke: work-queue-workflow
tags: []
---
# Work-Queue Workflow

Operating principle: **humans steer, agents execute**.
Stage-specific rules live in `.claude/skills/workspace-hub/stages/stage-NN-*.md`
and are auto-loaded by `start_stage.py` at stage entry.

## Canonical Terminology

| Term | Canonical meaning |
|------|------------------|
| **WRK session** | Single Claude conversation bounded by `/clear` or context reset |
| **WRK stage** | One of the 20 numbered lifecycle stages (Stage 1–20) |
| **Phase** | Sub-unit within a stage |
| **Checkpoint** | Snapshot artifact written at end of a WRK session (`checkpoint.yaml`) |

Violations: do NOT use "session" to mean "stage"; "phase" to mean "stage"; "step" to mean "stage".

## Stage Gate Policy (Hard Gates)

| Stage | Name | Gate | Exit Artifact |
|-------|------|------|---------------|
| 1 | Capture | **HARD** | `user-review-capture.yaml` (`scope_approved: true`) |
| 5 | User Review Plan Draft | **HARD** | `user-review-plan-draft.yaml` |
| 7 | User Review Plan Final | **HARD** | `plan-final-review.yaml` (`confirmed_by` human) |
| 17 | User Review Close | **HARD** | `user-review-close.yaml` |
| 2–4, 6, 8–16, 18–20 | All other stages | auto | — (pause on R-27 trigger) |

**R-25 (Hard gate):** Stages 1, 5, 7, 17 — agent MUST STOP and wait. Silence ≠ approval.

**R-26 (Continue):** After Stage 7 approval → execute Stages 8–16 without asking.
Check deterministically: `scripts/work-queue/is-human-gate.sh <N>` (exit 0=STOP, exit 1=CONTINUE).

**R-27 (Conditional pause):** Any auto-proceed stage with P1 finding, scope change, or
irreversible risk → pause, describe risk, await direction.

**Stage banner rule (all 20 stages):**
```
── Stage N: <Name> ── START
── Stage N: <Name> ── DONE
── Stage N: <Name> ── WAITING\nDo you approve? (yes/no)
```
Canonical names: 1 Capture | 2 Resource Intelligence | 3 Triage | 4 Plan Draft |
5 User Review - Plan Draft | 6 Cross-Review | 7 User Review - Plan Final |
8 Claim/Activation | 9 Work-Queue Routing | 10 Work Execution |
11 Artifact Generation | 12 TDD/Eval | 13 Agent Cross-Review |
14 Verify Gate Evidence | 15 Future Work Synthesis | 16 Resource Intelligence Update |
17 User Review - Close | 18 Reclaim | 19 Close | 20 Archive

## Plan-Mode Gates

EnterPlanMode before writing any artifact at:

| Stage | Trigger |
|-------|---------|
| 4 Plan Draft | Before first lifecycle HTML write |
| 6 Cross-Review | Before synthesizing 3-provider verdicts |
| 10 Work Execution | Before implementation file writes |
| 13 Agent Cross-Review | Before recording implementation verdict |

## Orchestrator Team Pattern

**Hard rule:** No WRK may be fully executed in a single Claude conversation.
Each stage (or stage group) must be a separate agent task.

- Any subtask requiring >3 file reads or >50 lines of output → delegate via TaskCreate
- Orchestrator accumulates summaries/pass-fail signals — never raw file content
- Scope-discovery-first (R-28): find ALL items first, then spawn agents at once

## Visual Reference

Stage flow diagram (mermaid): `.claude/docs/wrk-lifecycle-stages.md`

## Source of Truth

- Process contract: `.claude/work-queue/process.md`
- Execution workflow: `coordination/workspace/work-queue/SKILL.md`
- Gate enforcement: `workspace-hub/workflow-gatepass/SKILL.md`
- Stage micro-skills: `.claude/skills/workspace-hub/stages/stage-NN-*.md` (auto-loaded by start_stage.py)
- Stage contracts: `scripts/work-queue/stages/stage-NN-*.yaml`
- Gate hook: `scripts/work-queue/gate_check.py`

## Practical Lessons

- Stages 8, 19, 20 (Claim/Close/Archive) are autonomous — run scripts without asking.
- Use shared scripts (`session.sh`, `work.sh`, `plan.sh`, `execute.sh`, `review.sh`).
- Per-agent coverage gaps are workflow defects even if aggregate metrics pass.
- Scripts over LLM: `.claude/rules/patterns.md §Scripts Over LLM Judgment` (25% rule).
- Stage 17 rolling scope cap: absorb only WRK-NNN's own HIGH violations; pre-existing →
  `evidence/deferred-findings.yaml` (`disposition: new-wrk`).

## Feature WRK Lifecycle

See: @.claude/docs/feature-wrk-lifecycle.md

Feature WRK (`type: feature`) → Stage 7 exit → `new-feature.sh WRK-NNN` (Stage 9b) →
children run their own lifecycles → all children `archived` → `close-item.sh` closes feature.
