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
- User says approval was done "via label", "label-based", or similar, meaning the live GitHub `status:plan-approved` label is the approval source
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

If the user says approval was label-based and the pre-check shows `status:plan-approved` is already present, do not redundantly edit labels. Treat the label as the approval source, sync local artifacts to it, and document that source in the marker/comment.

## Mid-stream revalidation rule

If an earlier handoff or recommendation said to remove a stale approval marker or keep the issue in `status:plan-review`, revalidate live GitHub immediately before staging/committing. If the live issue now carries `status:plan-approved`, switch course to approval-state sync instead of committing a rollback/review-state change.

Use the live `status:plan-approved` label as the approval source in the local marker only when it is verified directly in the current session. Prefer neutral wording such as:

```text
Approved by: user
Approval source: live GitHub issue label status:plan-approved observed during approval-state sync
Approved at: <current UTC timestamp>
Issue: #<issue>
Plan: <plan path>
Review evidence: <provider verdict summary and artifact paths>
```

After the sync, update any stale plan sections that still describe older MAJOR/UNAVAILABLE review artifacts or stale approval drift. Otherwise the plan can contradict the restored approval marker and trigger another review/governance churn cycle.

When committing from a dirty checkout, stage only the issue's approval-sync surfaces. If a shared index file (for example `docs/plans/README.md`) also contains unrelated dirty rows, temporarily restore those unrelated rows to HEAD before staging, commit the narrow sync, then restore the user's unrelated local dirt afterward.

### Concurrent-git / push verification gotchas

Approval-sync work often happens in a busy multi-agent checkout. Before committing:
- If `git add`/`git commit` fails on `.git/index.lock`, do not immediately delete the lock blindly. First run `ps -ef | grep -E 'git( |$)' | grep -v grep` and identify live git/status processes.
- If a live `git status` or other git process is still running, wait briefly or let it finish; only remove `.git/index.lock` after confirming no relevant git process remains.
- If `git push` reports `remote rejected ... cannot lock ref ... is at <new> but expected <old>`, treat it as an ambiguous push outcome, not an automatic failure. Immediately verify with `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`. If both hashes match, the push actually landed and no retry is needed.
- Keep final verification anchored to the four approval surfaces plus remote hash: GitHub label, approval marker, plan header, README row, and `origin/main == HEAD`.

## Example artifact updates
- `.planning/plan-approved/2269.md`
- `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
- `docs/plans/README.md`

## Output expectation
After sync, local and remote state should agree that the issue is approved and ready for execution.
