---
name: user-approved-plan-state-sync
description: Reconcile GitHub and local repo state when a plan has already been user-approved but local planning artifacts still lag.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [github, planning, governance, approval-state, drift-cleanup]
---

# User-Approved Plan State Sync

Use when a GitHub issue already reflects user approval (`status:plan-approved`) but local planning artifacts still show older state (`plan-review` or missing marker).

## When to use
- User says they already approved the recommendation/plan
- GitHub issue already has `status:plan-approved`
- Local repo is missing one or more of:
  - `.planning/plan-approved/<issue>.md`
  - local plan header `> **Status:** plan-approved`
  - `docs/plans/README.md` row with `plan-approved`

## Goal
Do approval-state reconciliation, not rollback. Bring local state up to the already-approved GitHub state.

## Steps
1. Verify live GitHub state first.
   - `gh issue view <issue> --json number,title,labels,state,url`
   - Confirm `status:plan-approved` is present and the issue is still open.

2. Verify local drift surfaces.
   - Check `.planning/plan-approved/<issue>.md`
   - Check the canonical plan file header status
   - Check the `docs/plans/README.md` row status

3. If GitHub is already `status:plan-approved`, sync local state instead of downgrading labels.
   - Create/update `.planning/plan-approved/<issue>.md`
   - Update local plan header from `plan-review` to `plan-approved`
   - Update the `docs/plans/README.md` row from `plan-review` to `plan-approved`

4. Post a short GitHub comment noting approval-state sync.
   Include that local approval evidence was reconciled to match live GitHub approval state.

5. Re-verify all four surfaces.
   - GitHub labels
   - local approval marker
   - plan header
   - README row

## Important rule
Do not roll an issue back to `status:plan-review` just because the local marker or README row lags, if the user has already approved and GitHub is already correctly at `status:plan-approved`.

## Example artifact updates
- `.planning/plan-approved/2269.md`
- `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
- `docs/plans/README.md`

## Output expectation
After sync, local and remote state should agree that the issue is approved and ready for execution.
