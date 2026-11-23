# Archived Skill: `overnight-plan-artifact-placement-drift-reconciliation`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-plan-artifact-placement-drift-reconciliation`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-plan-artifact-placement-drift-reconciliation`
Consolidation date: 2026-04-29

---

---
name: overnight-plan-artifact-placement-drift-reconciliation
description: Reconcile overnight planning waves where Claude workers advance GitHub issue state but the expected plan/review artifacts are missing from the designated external worktree because the worker wrote from a sandbox/in-repo worktree and pushed directly to the branch.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [overnight, planning, claude, worktree, github, artifact-drift]
---

# Overnight plan artifact placement drift reconciliation

Use when:
- overnight Claude planning workers were launched from an external worktree
- the worker claims success and GitHub labels/comments advanced
- expected `docs/plans/...` or `scripts/review/results/...` files are missing from the original worktree
- you suspect the worker used a sandbox worktree or pushed directly to the remote branch

## Symptom pattern

Typical signals:
- worker output says an issue is now `status:plan-review`
- GitHub issue comments contain plan/review summaries
- local external worktree does not contain the claimed plan/review artifacts
- `git status` in the external worktree does not reflect the worker's claimed changes
- a branch tip exists on origin that your local worktree has not incorporated

## What happened

Claude may execute from an in-sandbox checkout (for example under `.claude/worktrees/...`) rather than the external `/mnt/local-analysis/worktrees/...` path you launched from. It can still push a valid commit to the intended branch and update GitHub issue labels/comments, leaving the original external worktree stale.

This is not necessarily worker failure. It is artifact-placement drift.

## Verification order

Do NOT trust only local file existence. Verify in this order:

1. GitHub live state
- `gh issue view <issue> --json labels,comments,url,title`
- confirm whether `status:plan-review` or `status:plan-approved` actually changed
- confirm the latest issue comment references the claimed plan path and review verdicts

2. Remote branch state
- `git ls-remote --heads origin <branch>`
- capture the branch SHA the worker claims to have pushed

3. Remote commit contents
- `git show --stat <sha>`
- confirm exact plan/review artifact paths in the pushed commit
- if needed: `git show <sha>:docs/plans/<file>` and `git show <sha>:scripts/review/results/<file>`

4. Local external worktree state
- only after steps 1-3, check whether the files exist locally
- if they do not exist locally but do exist in the remote commit, classify as placement drift

## Decision rule

Classify outcomes as:
- Clean success: GitHub + remote commit + local worktree all agree
- Artifact-placement drift: GitHub + remote commit agree, local worktree missing/stale
- Worker failure: GitHub did not advance and no remote commit contains the claimed artifacts
- Governance drift: labels advanced but artifact evidence is incomplete or inconsistent

## Recovery actions

If placement drift is confirmed:
1. Do not rerun the planning worker immediately.
2. Record the remote SHA and exact artifact paths.
3. Reconcile the external worktree by fetching/resetting, cherry-picking, or rebuilding the worktree from the updated branch.
4. Only after reconciliation should you launch implementation from those plans.
5. In status reporting, say: "GitHub state verified; artifact placement drift detected; local worktree reconciliation required."

## Why this matters

Without this check, you can mistakenly conclude:
- the worker failed when it actually succeeded remotely
- the plan is missing when it exists on the branch
- the next implementation wave can start from a stale worktree

## Minimal command bundle

```bash
gh issue view 2463 --json labels,comments,url,title
git ls-remote --heads origin nightly/2460-2465-planwave
git show --stat <sha>
git show <sha>:docs/plans/<expected-plan>.md | sed -n '1,40p'
```

## Notes

This pattern was observed in a workspace-hub overnight 4-worker planning wave where:
- issues moved to `status:plan-review`
- comments were posted correctly
- some artifacts existed only in a remote branch commit from a sandbox worktree
- the original external worktree remained stale
