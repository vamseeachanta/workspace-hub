---
name: work-queue-orchestrator
description: Unified orchestrator for the 20-stage WRK lifecycle — dispatch, gate enforcement, and stage transitions
version: 1.0.0
updated: 2026-03-22
category: workspace-hub
type: skill
wrk_ref: WRK-5110
related_skills:
  - work-queue
  - plan-mode
capabilities:
  - stage-dispatch
  - gate-enforcement
  - canonical-stage-mapping
requires:
  - scripts/work-queue/dispatch-run.sh
  - scripts/work-queue/exit_stage.py
  - scripts/work-queue/verify-gate-evidence.py
tags: [orchestrator, lifecycle, stages]
---

# Work-Queue Orchestrator

Unified entry point for the 20-stage WRK lifecycle.

## Dispatch

`scripts/work-queue/dispatch-run.sh WRK-NNN`

## References

- [Stage Gate Policy](references/stage-gate-policy.md)
- [Stage Transitions](references/stage-transitions.md)
- [Stage Mapping](references/stage-mapping.yaml) — canonical stage-number to folder-name
- [Hooks Schema](references/hooks-schema.yaml)

## Scripts

- `scripts/generate-stage-mapping.py` — regenerate canonical mapping

## Constraints

See [hooks.yaml](hooks.yaml) for no-bypass rules.

## Source of Truth

Stage contracts: `.claude/skills/workspace-hub/stages/stage-NN-*/contract.yaml` | Stage skills: `.claude/skills/workspace-hub/stages/stage-NN-*/SKILL.md` | Gates: `scripts/work-queue/exit_stage.py`
