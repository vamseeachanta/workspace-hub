---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.0
updated: 2026-03-03
category: workspace-hub
triggers:
  - workflow gatepass
  - wrk gate enforcement
  - lifecycle gate
  - close gate evidence
related_skills:
  - workspace-hub/session-start
  - coordination/workspace/work-queue
  - workspace-hub/session-end
  - workspace-hub/wrk-lifecycle-testpack
capabilities:
  - lifecycle-gate-enforcement
  - evidence-contract
  - close-readiness-audit
requires:
  - .claude/work-queue/process.md
  - scripts/work-queue/verify-gate-evidence.py
invoke: workflow-gatepass
---
# Workflow Gatepass

Use this skill whenever a WRK item is being progressed through execution and close.
It makes the lifecycle sequence explicit and blocks bypass behavior.

## Required Lifecycle Chain

1. `/session-start` run and briefing emitted.
2. WRK selected via `/work` or explicit WRK ID from queue.
3. Resource Intelligence evidence created.
4. Plan drafted and reviewed.
5. User approval explicitly names WRK ID.
6. Claim evidence created and valid.
7. Execute with examples, variation tests, and integrated/repo tests.
8. Reclaim stage used if continuity breaks.
9. Future-work evidence created for deferred findings.
10. Close only after gate evidence verification.
11. Archive only after merge/sync and archive evidence pass.

## No-Bypass Rules

- No implementation before WRK item + plan + explicit WRK approval.
- No close without gate evidence and `integrated_repo_tests` count in `[3,5]`.
- No archive when queue validation fails or merge/sync evidence is missing.

## Close Gate Minimum

Before close, require all of:

- `plan gate` passed
- `TDD gate` passed
- `integrated test gate` passed (3-5 pass records)
- `legal gate` passed
- `cross-review gate` passed
- `resource-intelligence gate` passed
- `reclaim gate` evaluated (pass or n/a with reason)
- `future-work gate` passed
- `archive-readiness gate` passed or deferred with follow-up WRK

## Evidence Locations

All stage evidence is stored under:

`assets/WRK-<id>/evidence/`

Recommended files:
- `resource-intelligence.yaml`
- `claim.yaml`
- `execute.yaml`
- `reclaim.yaml`
- `future-work.yaml`
- `close.yaml`
- `archive.yaml`

