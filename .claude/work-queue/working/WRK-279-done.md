---
id: WRK-279
title: "Audit & govern the /mnt/ace/ Codex relocation plan"
status: complete
priority: high
complexity: medium
compound: false
created_at: 2026-02-20T00:00:00Z
target_repos:
  - workspace-hub
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: true
percent_complete: 90
brochure_status: n/a
---

# Audit & govern the /mnt/ace/ Codex relocation plan

## What

Codex generated a 10-step "drastic relocation" migration checklist that proposes moving ALL legacy
project roots (`2H/`, `0_mrv/`, `Production/`, `umbilical/`) into a new
`docs/clients/{client}/projects/{project}/` hierarchy. 17 projects in `2H/` are already partially
migrated; ~200+ remain untouched. No human approval gate was in place before the plan was drafted.

## Why

Without a decision record, further automated or agentic migrations could proceed unchecked,
creating confusion and broken references. A governance decision must come first — before any
further files are relocated.

## Acceptance Criteria

- [x] Read `/mnt/ace/docs/_templates/MIGRATION_CHECKLIST.md` and `GOVERNANCE.md`
- [x] Inventory what has already moved (17 × `README_MIGRATED.md` in `2H/`)
- [x] Assess whether full migration is desired, deferred, or cancelled
- [x] Produce `/mnt/ace/docs/REORGANISATION_DECISION.md` with clear proceed/pause/cancel decision
- [x] No further files relocated until decision record is in place
- [x] Verify existing `README_MIGRATED.md` pointers are accurate — **ALL 17 BROKEN** (target dir never created)

## Agentic AI Horizon

- This is a governance gate — agentic execution is exactly what created the problem. Human
  decision-making is the correct approach here.
- The decision record itself is the deliverable; it enables WRK-281 to proceed safely.

---
*Source: Plan — /mnt/ace/ Document Organisation & ABS Standards Acquisition*
