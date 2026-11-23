# Archived Skill: `live-writer-branch-cleanup-guard`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/live-writer-branch-cleanup-guard`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/live-writer-branch-cleanup-guard`
Consolidation date: 2026-04-29

---

---
name: live-writer-branch-cleanup-guard
description: Guardrails for multi-repo sync and branch cleanup when workspace-hub or another shared repo has active writer sessions, worktree-backed branches, or unrelated-history branches.
version: 1.0.0
source: session-learned
---

# Live-Writer Branch Cleanup Guard

Use when:
- doing repo-wide sync + branch cleanup across workspace-hub repos
- a shared repo keeps becoming dirty between checks
- many branches are worktree-backed or created by overnight agents

## Core pattern

1. Commit and push dirty repos first.
2. Before mass branch cleanup, check for active writer sessions:
   - `ps -ef | grep claude`
   - `ps -ef | grep '[g]it'`
   - repeated `git status --short`
3. If a repo becomes dirty again between checks, classify it as a live-writer repo.
4. Do not do broad merge/delete passes on live-writer repos until the writers stop.
5. Use temporary worktrees for branch-to-default merge attempts when the main working tree is dirty or on a non-default branch.

## Branch triage rules

### Safe to delete
- already merged branches with shared history
- stale worktree-agent branches not attached to active worktrees
- old local aliases like `master` in a `main`-default repo once confirmed merged

### Do not auto-merge
- branches that fail with `fatal: refusing to merge unrelated histories`
- branches with real content conflicts
- branches currently attached to active worktrees
- branches in repos with active concurrent writer sessions

## Interpretation of common failures

- `fatal: refusing to merge unrelated histories`
  - Treat as separate lineage/import branch.
  - Do not auto-merge to main.
  - Report for manual triage.

- `error: cannot delete branch '<name>' used by worktree`
  - Branch is active.
  - Skip deletion.
  - Clean the worktree first, then retry later.

- repo gets dirty again right after commit/push
  - Usually another agent/process is still writing.
  - Stop mass cleanup in that repo and finish other repos first.

## Practical order of operations

1. Audit repos: default branch, dirty state, ahead/behind, branch inventory.
2. Commit/push all dirty repos.
3. Prune obviously merged branches in quiet repos.
4. Attempt merges only for branches with shared history and no active worktree attachment.
5. Leave shared-control repos like workspace-hub for a dedicated quiet window.

## Why this exists

A large multi-repo cleanup run showed that the biggest blocker was not git itself but active background Claude/worktree activity. Treating live-writer repos as a special case avoids false cleanup attempts, repeated dirty-state churn, and unsafe branch operations.
