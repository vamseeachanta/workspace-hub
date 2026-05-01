# Archived Skill: `user-approved-plan-state-sync`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/user-approved-plan-state-sync`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/user-approved-plan-state-sync`
Consolidation date: 2026-04-29

---

---
name: user-approved-plan-state-sync
description: Reconcile GitHub and local repo state when a plan has been user-approved, including direct approval messages that require creating the local marker and moving the issue to status:plan-approved.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [github, planning, governance, approval-state, drift-cleanup]
---

# User-Approved Plan State Sync

Use when a plan has been user-approved and GitHub/local planning surfaces need to be synchronized. This includes both cases where the GitHub issue already reflects approval (`status:plan-approved`) and cases where the user has just explicitly approved the issue and asks to create the approval marker / move the label.

## When to use
- User says they approve an issue/plan and asks to create `.planning/plan-approved/<issue>.md`, move labels to `status:plan-approved`, or proceed to implementation.
- User says they already approved the recommendation/plan.
- User says a short continuation phrase like "continue with recommendation" immediately after an approval-shortlist response that named exactly one "approve now" candidate. Treat this as approval for that one candidate only; do not infer approval for issues explicitly categorized as not-ready/revision/drift.
- User says approval was done "via label", "label-based", or similar, meaning the live GitHub `status:plan-approved` label is the approval source.
- GitHub issue already has `status:plan-approved`.
- Local repo is missing one or more of:
  - `.planning/plan-approved/<issue>.md`
  - local plan header `> **Status:** plan-approved`
  - `docs/plans/README.md` row with `plan-approved`

## Goal
Do approval-state synchronization, not rollback. Bring GitHub labels, the local marker, canonical plan status, and the planning index into agreement that the issue is approved and ready for implementation.

## Steps
1. Verify live GitHub state first.
   - `gh issue view <issue> --json number,title,labels,state,url`
   - Confirm the issue is still open.
   - If `status:plan-approved` is already present, treat the live label as the approval source.
   - If the issue is still `status:plan-review` but the current user message explicitly approves it, treat the user message as the approval source and move the label to `status:plan-approved` after local marker creation.

2. Verify local drift surfaces.
   - Check `.planning/plan-approved/<issue>.md`
   - Check the canonical plan file header status
   - Check the `docs/plans/README.md` row status

3. Synchronize approval state.
   - Create/update `.planning/plan-approved/<issue>.md`.
   - Record the approval source precisely:
     - current explicit user message, if the user approved in this session; or
     - live GitHub `status:plan-approved` label, if label-based approval was already present.
   - Update local plan header from `draft`/`plan-review` to `plan-approved`.
   - Update the `docs/plans/README.md` row from `draft`/`plan-review` to `plan-approved (implementation ready)` when implementation is now authorized.
   - If GitHub is not already approved and the user explicitly approved now, run `gh issue edit <issue> --add-label status:plan-approved --remove-label status:plan-review`.
   - If GitHub is already `status:plan-approved`, sync local state instead of redundantly editing labels.

4. Commit and push the approval-sync surfaces before posting the GitHub sync comment when possible.
   - Stage only the marker, canonical plan, and planning index rows for that issue.
   - Push the commit so the comment can cite a durable commit hash.
   - If unrelated local dirt remains, keep it out of the commit and mention it only as unrelated checkout state in the final response if relevant.

5. Post a short GitHub comment noting approval-state sync.
   Include that local approval evidence was reconciled to match live GitHub approval state.
   Include the approval-sync commit hash after it is pushed.
   If the issue is now execution-ready, include the next concrete TDD execution package in the same comment: target test file(s), implementation script/module, config/artifact outputs, and required validation/review gates. This turns the approval-sync comment into a handoff that Codex/Claude can immediately execute without re-discovery.

6. Re-verify all four surfaces plus the remote hash.
   - GitHub labels
   - local approval marker
   - plan header
   - README row
   - `git ls-remote origin refs/heads/main` matches local `HEAD` for the sync commit

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
- If a live `git status`, `git worktree add`, `git reset`, or other git process is still running, wait briefly or let it finish; only remove `.git/index.lock` after confirming no relevant git process remains.
- If `git push` is rejected as non-fast-forward, immediately run `git fetch origin main` and inspect `git show --stat --oneline origin/main` plus the remote versions of the marker/plan/README row. Another agent may already have pushed an equivalent approval-sync commit. If `origin/main` already contains the required approval surfaces, treat that remote commit as the durable sync, post the GitHub comment citing it, and do not continue a duplicate local rebase/commit.
- If a duplicate local approval-sync commit is already in progress while `origin/main` has equivalent surfaces, preserve unrelated dirt first, then either `git rebase --abort` or hard-align only after confirming no unique local work would be lost. Prefer using the remote commit hash as source of truth over forcing a duplicate push.
- If `git push` reports `remote rejected ... cannot lock ref ... is at <new> but expected <old>`, treat it as an ambiguous push outcome, not an automatic failure. Immediately verify with `git rev-parse HEAD` and `git ls-remote origin refs/heads/main`. If both hashes match, the push actually landed and no retry is needed.
- Keep final verification anchored to the four approval surfaces plus remote hash: GitHub label, approval marker, plan header, README row, and the pushed/observed remote commit hash. `origin/main == HEAD` is ideal, but in a dirty/concurrent checkout it is acceptable for `origin/main` to contain the verified approval-sync commit while local `HEAD` has unrelated divergence; report that distinction explicitly.

## Example artifact updates
- `.planning/plan-approved/2269.md`
- `docs/plans/2026-04-15-issue-2269-openfoam-v2312-baseline-workflow-and-validation.md`
- `docs/plans/README.md`

## Output expectation
After sync, local and remote state should agree that the issue is approved and ready for execution.
