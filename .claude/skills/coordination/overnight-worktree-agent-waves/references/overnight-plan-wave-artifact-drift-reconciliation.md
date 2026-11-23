# Archived Skill: `overnight-plan-wave-artifact-drift-reconciliation`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-plan-wave-artifact-drift-reconciliation`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-plan-wave-artifact-drift-reconciliation`
Consolidation date: 2026-04-29

---

---
name: overnight-plan-wave-artifact-drift-reconciliation
description: Reconcile overnight planning waves when Claude workers move GitHub issues to status:plan-review but local artifacts are missing, split across sandbox worktrees, or only present on a pushed remote branch.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [overnight, planning, github, worktree, artifact-drift, claude]
---

# Overnight plan-wave artifact drift reconciliation

Use when:
- running parallel overnight planning-only Claude workers
- workers are supposed to produce `docs/plans/...` files and `scripts/review/results/...` artifacts
- a worker claims success and/or advances the GitHub issue to `status:plan-review`
- but the orchestrator cannot find the claimed files in the active worktree

## Problem pattern

In overnight planning waves, a worker can successfully:
- post GitHub comments
- add `status:plan-review`
- claim plan/review artifacts exist

while the orchestrator's active worktree still does not contain those artifacts.

Observed causes:
1. the worker ran in a different in-sandbox worktree than the external worktree path named in the prompt
2. the worker pushed artifacts directly to a remote branch without updating the orchestrator-visible checkout
3. shared-index / multi-worker serialization races bundled multiple workers' files into one commit with mixed attribution
4. GitHub state advanced even though local artifact normalization never happened in the expected checkout

## Required verification order

For each completed worker, verify these three surfaces separately:

1. GitHub live state
- `gh issue view <n> --json number,title,labels,url`
- `gh issue view <n> --comments`
- confirm whether `status:plan-review` was actually applied
- capture the worker's own provenance notes from comments

2. Local active-worktree artifact state
- search `docs/plans/*<issue>*`
- search `scripts/review/results/*<issue>*`
- do not assume success just because the worker log says files were written

3. Remote-branch / commit state
- `git ls-remote --heads origin <branch>`
- `git log --oneline --decorate -n <k>`
- `git show --stat <sha>`
- if needed, `git show <sha>:path/to/file`
- use this to prove whether the artifacts exist only in the remote branch or in a different commit than expected

## Classification rule

After verification, classify each issue as one of:

- fully verified
  - GitHub label/comment correct
  - local plan + review artifacts present in the active worktree

- GitHub-advanced, local-artifact drift
  - GitHub label/comment correct
  - local artifacts missing from active worktree
  - no remote proof yet

- remote-branch-only artifact provenance
  - GitHub label/comment correct
  - local artifacts missing from active worktree
  - remote branch / commit proves the artifacts exist there

- blocked / not promoted
  - worker finished but issue correctly stayed out of `status:plan-review`
  - usually due to MAJOR review findings

Do not describe `status:plan-review` items as cleanly verified unless local or remote artifact provenance has been checked.

## Reporting rule

When summarizing progress for the user, explicitly separate:
- GitHub state verified
- local artifact state verified
- remote-branch artifact state verified

Good summary style:
- fully verified: #2459, #2460, #2461
- GitHub label verified, artifact reconciliation still needed: #2458, #2462, #2465
- remote-branch-only artifact provenance confirmed: #2463, #2464

## Worktree / sandbox lesson

If a worker mentions:
- in-sandbox worktree relocation
- direct remote push
- shared-index race
- cleanup of a different worktree than the one named in the prompt

trust that as a provenance warning and perform branch-level verification immediately.

## Operational response

If drift is found:
1. do not relaunch the same issue immediately
2. capture the current GitHub state first
3. prove whether artifacts exist in remote history
4. only then decide whether the issue needs:
   - governance cleanup only
   - local checkout reconciliation
   - re-planning
   - re-review

## Reusable takeaway

For overnight planning waves, GitHub status transitions are not enough. Always audit GitHub, local worktree, and remote branch separately before calling a worker result clean.
