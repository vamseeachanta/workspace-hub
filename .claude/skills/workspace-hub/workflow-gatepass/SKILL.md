---
name: workflow-gatepass
description: 'Enforce WRK lifecycle gatepass from session start through close/archive
  with machine-checkable evidence requirements and explicit no-bypass rules.

  '
version: 1.0.6
updated: 2026-03-07
category: workspace-hub
triggers:
- workflow gatepass
- wrk gate enforcement
- lifecycle gate
- close gate evidence
related_skills:
- session-start
- work-queue
- session-end
- wrk-lifecycle-testpack
capabilities:
- lifecycle-gate-enforcement
- evidence-contract
- close-readiness-audit
requires:
- .claude/work-queue/process.md
- scripts/work-queue/verify-gate-evidence.py
- scripts/work-queue/parse-session-logs.sh
- scripts/review/orchestrator-variation-check.sh
- scripts/work-queue/start_stage.py
- scripts/work-queue/exit_stage.py
- scripts/work-queue/gate_check.py
- scripts/work-queue/stages/stage-NN-*.yaml
invoke: workflow-gatepass
tags: []
see_also:
- workflow-gatepass-required-lifecycle-chain
- workflow-gatepass-stage-15-to-stage-17-rule-next-work-disposition
- workflow-gatepass-visual-reference
- workflow-gatepass-route-consistency-abc
- workflow-gatepass-no-bypass-rules
- workflow-gatepass-close-gate-minimum
- workflow-gatepass-evidence-locations
- workflow-gatepass-reusable-scripts
- workflow-gatepass-operational-lessons-wrk-690
---

# Workflow Gatepass

## Sub-Skills

- [Required Lifecycle Chain](required-lifecycle-chain/SKILL.md)
- [Stage 15 to Stage 17 Rule (Next-Work Disposition)](stage-15-to-stage-17-rule-next-work-disposition/SKILL.md)
- [Visual Reference](visual-reference/SKILL.md)
- [Route Consistency (A/B/C)](route-consistency-abc/SKILL.md)
- [No-Bypass Rules](no-bypass-rules/SKILL.md)
- [Close Gate Minimum](close-gate-minimum/SKILL.md)
- [Evidence Locations](evidence-locations/SKILL.md)
- [Reusable Scripts](reusable-scripts/SKILL.md)
- [Operational Lessons (WRK-690)](operational-lessons-wrk-690/SKILL.md)
