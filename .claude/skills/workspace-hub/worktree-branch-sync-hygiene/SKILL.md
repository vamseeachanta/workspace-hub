---
name: worktree-branch-sync-hygiene
version: 1.0.0
category: workspace-hub
description: Class-level branch, worktree, dirty-main, stash, sync, and hook hygiene for workspace-hub style multi-repo work.
tags: [git, worktree, sync, branch-hygiene]
---

# Worktree Branch Sync Hygiene

## When to Use
Use when promoting work from dirty main/worktrees, cleaning blocked branches, reconciling sync churn, handling pre-push/hook drift, or preserving tags/changes during cleanup.

## Class-Level Workflow
1. Inventory dirty state, untracked files, stashes, branches, worktrees, and remotes before moving anything.
2. Preserve recoverability with tags/stashes/patch files before branch cleanup.
3. Separate narrow fix promotion from broad sync/root churn.
4. Verify hook paths and real installed hook shape, not just intended config.
5. After sync, re-check for concurrent writer blocks before declaring clean.
6. Treat issue closeout as a single transaction: test, commit, push, merge/sync, branch disposition, worktree removal, clean-state proof, then close the issue. Push-to-origin and cleanup are not follow-up chores; they must happen in the same closeout window before/with issue closure. Never close first and defer cleanup to a later sweep. See `references/transactional-issue-closeout-cleanup.md`.
7. Serialize writer closeout operations with a repo-level lock/mutex; do not let multiple agents commit, pull/rebase/merge, push, prune branches, or remove worktrees concurrently from the same checkout.
8. Do not use `rm -f .git/index.lock` in normal retry loops. Only remove an index lock under explicit stale-lock recovery conditions: closeout lock held, no active git process, lock older than threshold, missing owner process, and logged operator recovery.
9. After docs-only or handoff commits from a clean isolated worktree, re-check for hook-generated dirt before declaring exit clean. Workspace-hub hooks can update generated files such as `scripts/testing/coverage-results.json` even when the pushed commit is docs-only; restore unintended generated dirt, then verify `HEAD == origin/main` and `git status --short` is empty.
10. If a merge/push happened before context compaction or tool output was truncated, re-verify `origin/main`, integration worktree cleanliness, dirty-root preservation, exact validation counts, and any nonzero legal/security check before giving a final report. See `references/post-compaction-merge-verification.md`.
11. Stale worktree cleanup must scan both `git worktree list` and filesystem worktree roots such as `.claude/worktrees/` for broken `.git` pointer files; registered-worktree cleanup alone can miss hundreds of MB of orphaned directories.
12. When inherited closeout debt already exists, run a non-destructive bulk recovery under the closeout lock: prune only branches merged into `origin/main`, preserve all unmerged branches with unique commits, remove only broken/unregistered worktree directories, commit generated evidence, then verify clean/synced state. See `references/bulk-closeout-debt-recovery.md`.
13. During preserved-branch PR sweeps, never treat “PR created” as “branch cleaned.” Merge and delete only after fresh GitHub evidence shows mergeable + required checks green. If CI/environment gates fail, stop, record exact failing check names/errors, leave local/remote branch intact, commit/push the ledger, and report the exact next unblock step. Do not rewrite preserved branches to rebase them during cleanup; if a branch is already contained in `origin/main`, prove `git rev-list --count origin/main..BR == 0` and delete without force-pushing. See `references/preserved-branch-pr-sweep-blockers.md`.
14. When asked why stale files/branches/unmerged commits/worktrees accumulated, perform an evidence-based closeout-debt RCA from reflog, worktree list, branch containment, stash list, provider/orchestrator logs, and GitHub issue/PR events. Separate remote landed state from local checkout state, and treat any active foreign rebase/merge as a blocker requiring explicit user approval before abort/continue/conflict resolution. See `references/concurrent-closeout-and-rebase-drift.md`.
15. For shared-root rebase recovery, use a read-only subagent to audit ownership/reflog/PR merge state before taking any destructive action. If the PR is already landed and the root is merely stale/behind, fast-forward under the closeout lock; write the recovery log from a clean isolated worktree; push the docs-only closeout commit; remove the temporary branch/worktree; then produce clean proof. See `references/subagent-assisted-rebase-recovery-closeout.md`.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `transactional-issue-closeout-cleanup`

- Session reference: `references/transactional-issue-closeout-cleanup.md`.
- Preserved insight: Issue closure must be transactional with push/merge, branch disposition, worktree removal, clean-state proof, and closeout evidence; also scan for broken filesystem worktrees not visible in `git worktree list`.

### `bulk-closeout-debt-recovery`

- Session reference: `references/bulk-closeout-debt-recovery.md`.
- Preserved insight: Recover inherited closeout debt by pruning only branches merged into `origin/main`, preserving unmerged unique branches, removing only broken/unregistered worktree dirs, committing evidence, and proving `HEAD == origin/main` with clean status.

### `preserved-branch-pr-sweep-blockers`

- Session reference: `references/preserved-branch-pr-sweep-blockers.md`.
- Preserved insight: During preserved-branch PR sweeps, stop on failing/pending required checks, keep the branch/PR open, commit blocker evidence, and never rewrite branches during cleanup; already-contained branches should be deleted only after proving zero unique commits versus `origin/main`.

### `post-compaction-merge-verification`

- Session reference: `references/post-compaction-merge-verification.md`.
- Preserved insight: When a merge/push happened before compaction or tool output was truncated, final reports must re-check `origin/main`, integration worktree cleanliness, dirty-root preservation, validation counts, and legal/security scan status from fresh commands.

### `concurrent-closeout-and-rebase-drift`

- Session reference: `references/concurrent-closeout-and-rebase-drift.md`.
- Preserved insight: Stale files/branches/worktrees accumulate when issue closure is separated from same-window push, branch/worktree disposition, and clean-state proof; when a foreign rebase disrupts a just-pushed closeout, report remote landed state separately from local checkout conflict state and do not abort/continue without approval.

### `subagent-assisted-rebase-recovery-closeout`

- Session reference: `references/subagent-assisted-rebase-recovery-closeout.md`.
- Preserved insight: Recover shared-root rebase drift by first dispatching a read-only subagent for ownership/reflog/PR-state evidence, then fast-forwarding only if the root is merely stale, writing the recovery log from a clean isolated worktree, pushing the docs-only commit, removing temporary branch/worktree, and proving clean sync.

### `blocked-branch-preserve-tag-cleanup`

- Former skill demoted to `references/blocked-branch-preserve-tag-cleanup.md`.
- Preserved insight: Safely clean stale local branches that cannot be merged by preserving them with local tags before deletion

### `clean-worktree-integration-from-dirty-main`

- Former skill demoted to `references/clean-worktree-integration-from-dirty-main.md`.
- Preserved insight: Land validated issue work from isolated worktrees when the main checkout is dirty by creating a fresh integration worktree, cherry-picking only implementation commits, re-running combined validation, and preparing push/closeout artifacts.

### `dirty-main-narrow-fix-promotion-with-stash-recovery`

- Former skill demoted to `references/dirty-main-narrow-fix-promotion-with-stash-recovery.md`.
- Preserved insight: Promote a narrow fix from a feature/worktree into workspace-hub main when main is dirty; verify label taxonomy before issue creation and recover safely when stash reapply conflicts.

### `full-branch-cleanup-and-worktree-hygiene`

- Former skill demoted to `references/full-branch-cleanup-and-worktree-hygiene.md`.
- Preserved insight: Track all dirty/untracked workspace-hub changes, merge stale branches into main, clean remote/local branches, and remove stale worktrees while preserving tracked nested gitlinks.

### `learned-git-worktree-hook-path-and-real-hook-shape-review`

- Former skill demoted to `references/learned-git-worktree-hook-path-and-real-hook-shape-review.md`.
- Preserved insight: Catch hook-installation and governance bugs that only appear in linked git worktrees or against the real generated hook shape, not simplified test fixtures.

### `live-writer-branch-cleanup-guard`

- Former skill demoted to `references/live-writer-branch-cleanup-guard.md`.
- Preserved insight: Guardrails for multi-repo sync and branch cleanup when workspace-hub or another shared repo has active writer sessions, worktree-backed branches, or unrelated-history branches.

### `repo-sync-deleted-remote-branch-and-unrelated-history-recovery`

- Former skill demoted to `references/repo-sync-deleted-remote-branch-and-unrelated-history-recovery.md`.
- Preserved insight: Recover multi-repo sync failures caused by deleted upstream branches, stale git index locks, and local branches with unrelated history to the remote default branch.

### `workspace-hub-sync-concurrent-writer-blocks`

- Former skill demoted to `references/workspace-hub-sync-concurrent-writer-blocks.md`.
- Preserved insight: Handle repository_sync cleanup when workspace-hub root is being mutated by concurrent Claude/Codex/Gemini sessions.

### `workspace-hub-sync-root-churn-catchup`

- Former skill demoted to `references/workspace-hub-sync-root-churn-catchup.md`.
- Preserved insight: Catch up workspace-hub root changes that continue to appear during repo sync because live review/agent processes keep writing files after commits

### `worktree-pre-push-bypass-for-tier1-checks`

- Former skill demoted to `references/worktree-pre-push-bypass-for-tier1-checks.md`.
- Preserved insight: Handle workspace-hub integration-branch pushes from isolated git worktrees when the pre-push hook incorrectly assumes sibling tier-1 repos exist under the worktree path.

### `interactive-issue-execution-worktree-guardrails`

- Former skill demoted to `references/interactive-issue-execution-worktree-guardrails.md`.
- Preserved insight: Execute approved GitHub issues in isolated worktrees with interactive Claude Code/Codex runs, while containing agent drift and salvaging progress when provider/runtime problems occur.

### `session-start-dirty-state-triage-with-background-agents`

- Former skill demoted to `references/session-start-dirty-state-triage-with-background-agents.md`.
- Preserved insight: Distinguish real implementation dirt from generated session-state churn when resuming a repo with active overnight/background agents.
