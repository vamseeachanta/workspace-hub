---
name: workflow-gatepass
description: >
  Enforce WRK lifecycle gatepass from session start through close/archive with
  machine-checkable evidence requirements and explicit no-bypass rules.
version: 1.0.2
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

1. Capture.
2. Resource Intelligence.
3. Triage.
4. Plan Draft.
5. User Review - Plan (Draft) with completed HTML opened in default browser.
6. Cross-Review.
7. User Review - Plan (Final) with completed HTML opened in default browser.
8. Claim / Activation.
9. Work-Queue Routing Skill (`/work` path).
10. Work Execution.
11. Artifact Generation.
12. TDD / Eval.
13. Verify Gate Evidence.
14. Future Work Synthesis.
15. Resource Intelligence Update.
16. User Review (close package) with completed HTML opened in default browser.
17. Reclaim (conditional when continuity breaks).
18. Close.
19. Archive.

## Route Consistency (A/B/C)

- All routes use the same canonical 19-stage lifecycle.
- Common mandatory gates for A/B/C: 1-9, 13-16, 18-19.
- Route A: lighter execution depth in stages 10-12 with one cross-review pass.
- Route B: standard execution depth in stages 10-12 with multi-provider cross-review.
- Route C: deeper execution/testing in stages 10-12 with stricter cross-review finding closure.

## No-Bypass Rules

- No implementation before WRK item + plan + explicit WRK approval.
- No user-review acceptance unless the completed HTML was opened in the default browser.
- No close without a per-WRK stage ledger in assets (`stage_evidence_ref`) covering stages 1-19.
- No close without gate evidence and `integrated_repo_tests` count in `[3,5]`.
- No archive when queue validation fails or merge/sync evidence is missing.

## Close Gate Minimum

Before close, require all of:

- `plan gate` passed
- `TDD gate` passed
- `integrated test gate` passed (3-5 pass records)
- `legal gate` passed
- `cross-review gate` passed
- `user-review html-open gate` passed for each user-review checkpoint
- `resource-intelligence gate` passed
- `reclaim gate` evaluated (pass or n/a with reason)
- `future-work gate` passed
- `archive-readiness gate` passed or deferred with follow-up WRK
- `stage evidence gate` passed (`stage_evidence_ref` file exists and includes stages 1-19)

## Evidence Locations

All stage evidence is stored under:

`assets/WRK-<id>/evidence/`

Recommended files:
- `resource-intelligence.yaml`
- `resource-intelligence-update.yaml`
- `claim.yaml`
- `execute.yaml`
- `reclaim.yaml`
- `future-work.yaml`
- `user-review-browser-open.yaml`
- `stage-evidence.yaml`
- `close.yaml`
- `archive.yaml`
