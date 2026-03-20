---
id: WRK-1155
title: "chore(harness): stage-07 P1-findings-resolved checker script"
status: done
route: A
priority: high
complexity: simple
compound: false
created_at: 2026-03-12T10:30:00Z
target_repos:
  - workspace-hub
commit:
spec_ref:
related:
  - WRK-1144
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: true
percent_complete: 100
brochure_status: n/a
computer: dev-primary
execution_workstations: [dev-primary]
plan_workstations: [dev-primary]
provider: claude
orchestrator: claude
cross_review: pending
stage_evidence_ref: .claude/work-queue/assets/WRK-1155/evidence/stage-evidence.yaml
subcategory: work-queue
category: harness
parent: WRK-1144
---
# chore(harness): Stage-07 P1 Findings Resolved Checker

## Mission

Create a deterministic script that verifies all P1 (critical) cross-review
findings are resolved before Stage 7 exit, making this gate binary (Level 2)
rather than LLM judgment.

## What

Script: `scripts/work-queue/check-p1-resolved.sh WRK-NNN`

- Read `assets/WRK-NNN/evidence/cross-review.yaml`
- For each reviewer: check `p1_count: 0` or finding has a `resolution:` entry
- Exit 0 if all P1s resolved; exit 1 listing unresolved P1s

## Acceptance Criteria

- [x] Script exits 0 when all P1 findings have resolutions
- [x] Script exits 1 and lists unresolved P1s when any remain
- [x] Integrated into stage-07-user-review-plan-final.yaml checklist
