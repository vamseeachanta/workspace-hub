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
9. Treat `.git/config.lock` warnings during branch/worktree cleanup as a separate stale-lock recovery path: verify no active Git owner, preserve the lock file outside the repo, remove it only under the closeout mutex, and then re-check branch deletion/containment. Under `set -euo pipefail`, guard zero-match process-count pipelines so recovery scripts do not abort before cleanup. See `references/stale-git-config-lock-closeout-recovery.md`.
10. After docs-only or handoff commits from a clean isolated worktree, re-check for hook-generated dirt before declaring exit clean. Workspace-hub hooks can update generated files such as `scripts/testing/coverage-results.json` even when the pushed commit is docs-only; restore unintended generated dirt, then verify `HEAD == origin/main` and `git status --short` is empty.
11. When the user asks to commit/push added files from a live workspace-hub branch, stage narrowly, verify the exact added files on the remote branch, and separate remote-pushed truth from fresh live-generated `.claude/state/session-signals` churn. If a new-branch pre-push hook is blocked only by unrelated tier-1 debt or topology assumptions, use the audited `GIT_PRE_PUSH_SKIP=1` path and say why. See `references/live-branch-added-files-push-with-generated-churn.md`.
11a. When the user specifically asks to commit **untracked files** from `main`, treat that as an untracked-only scope: inventory tracked dirt separately, secret-scan the untracked paths, stage only `git ls-files --others --exclude-standard`, fast-forward/merge `origin/main` without autostash/rebase, push, then prove `HEAD == origin/main` and `git ls-tree origin/main -- <paths>`. A push message of `Everything up-to-date` is acceptable only if remote proof shows the new commit/files are already on `origin/main`. See `references/untracked-only-main-commit-and-origin-verification.md`.
12. If a merge/push happened before context compaction or tool output was truncated, re-verify `origin/main`, integration worktree cleanliness, dirty-root preservation, exact validation counts, and any nonzero legal/security check before giving a final report. See `references/post-compaction-merge-verification.md`.
12. Stale worktree cleanup must scan both `git worktree list` and filesystem worktree roots such as `.claude/worktrees/` for broken `.git` pointer files; registered-worktree cleanup alone can miss hundreds of MB of orphaned directories.
13. When inherited closeout debt already exists, run a non-destructive bulk recovery under the closeout lock: prune only branches merged into `origin/main`, preserve all unmerged branches with unique commits, remove only broken/unregistered worktree directories, commit generated evidence, then verify clean/synced state. See `references/bulk-closeout-debt-recovery.md`.
14. During preserved-branch PR sweeps, never treat “PR created” as “branch cleaned.” Merge and delete only after fresh GitHub evidence shows mergeable + required checks green. If CI/environment gates fail, stop, record exact failing check names/errors, leave local/remote branch intact, commit/push the ledger, and report the exact next unblock step. Do not rewrite preserved branches to rebase them during cleanup; if a branch is already contained in `origin/main`, prove `git rev-list --count origin/main..BR == 0` and delete without force-pushing. See `references/preserved-branch-pr-sweep-blockers.md`.
15. When asked why stale files/branches/unmerged commits/worktrees accumulated, perform an evidence-based closeout-debt RCA from reflog, worktree list, branch containment, stash list, provider/orchestrator logs, and GitHub issue/PR events. Separate remote landed state from local checkout state, and treat any active foreign rebase/merge as a blocker requiring explicit user approval before abort/continue/conflict resolution. See `references/concurrent-closeout-and-rebase-drift.md`.
16. For shared-root rebase recovery, use a read-only subagent to audit ownership/reflog/PR merge state before taking any destructive action. If the PR is already landed and the root is merely stale/behind, fast-forward under the closeout lock; write the recovery log from a clean isolated worktree; push the docs-only closeout commit; remove the temporary branch/worktree; then produce clean proof. See `references/subagent-assisted-rebase-recovery-closeout.md`.
17. If PRs are merged and branches are zero-unique/contained but local Git operations hang (`git status`, `git diff`, `git worktree list`, or per-worktree clean checks), stop deletion and preserve evidence outside the repo rather than adding more ledger commits. Treat remote landed state and local cleanup state separately; zero-unique containment is not enough to remove a worktree whose dirt/index cannot be inspected. See `references/git-hang-closeout-preservation.md`.
18. When stale files/branches/unmerged commits/worktrees exist after issue closure, treat it as a process failure requiring evidence-based RCA and durable correction. Do not just clean; document why closure and cleanup diverged, preserve or remove each worktree in the same window as push/merge evidence, and do not stash/delete root dirt while active Claude/Hermes/Codex sessions have CWD in the repo unless explicitly approved. See `references/transactional-closeout-race-and-active-root-sessions.md`.
19. When broad Git commands hang during closeout and active root sessions exist, switch to bounded non-mutating probes, remove only independently proven safe zero-unique clean worktrees under the closeout lock, and report `remote landed/synced` separately from `local checkout clean`. A synced remote plus dirty live-owned root is an incomplete closeout blocker, not clean completion. See `references/active-root-closeout-blocker-bounded-probes.md`.
20. Do not use `ACTIVE_ROOT_CWD_COUNT == 0` as the only safety condition on a live Hermes control-plane checkout; passive shells/TUIs/viewers can keep CWD under root indefinitely. Classify active root processes into Git writers, artifact writers/owners, passive control sessions, and unknown owners. If `HEAD` and `origin/main` diverge while root is dirty, inspect local-only and remote-only commits and do not auto-merge/rebase/stash from the live root. See `references/root-session-wait-and-divergence-gate.md`.
21. When merging/deleting a stale branch that is substantively already on `origin/main` but whose history is not connected, use a clean temporary integration worktree and a `--no-ff` merge to tie history. If conflicts are only in generated/live session-state files and durable artifacts are identical on `origin/main`, resolve those generated-state conflicts with `--ours`, push the merge, prove `origin/main..origin/branch == 0`, delete the remote branch, fast-forward local `main`, then delete the local branch/worktree. Report synced remote state separately from unrelated live-root dirt. See `references/merge-stale-branch-with-generated-state-conflicts.md`.
22. After broad self-improvement or multi-repo commit/push sessions, expect final status to reveal new hook/provider/concurrent-worker dirt. Classify dirty paths before staging, secret-scan narrowly, commit verified deliverables separately from hook evidence, and never sweep-commit implementation dirt whose owning targeted test fails. Run a second fresh status pass after the final push/fetch because generated artifact families can appear immediately after an apparently clean snapshot; commit complete verified families (for example HTML/PDF/ZIP packs or refreshed caches) or preserve/report a blocker. Report `remote synced`, `local clean`, and `blocked dirty` as separate states. See `references/post-push-dirty-artifact-triage.md`.
23. Near a tool-call/context limit, do not create a final local commit unless you can immediately push and verify it. Treat each late-session commit as a mini-transaction: commit → push → fetch → prove `HEAD == origin/main` and clean status before starting optional cleanup. If one late untracked report remains and execution budget is low, leave it untracked and document it rather than ending with an unpushed commit. See `references/tool-budget-safe-final-push-verification.md`.
23a. If normal `git commit` or broad `git status` hangs in a shared live checkout but the staged change is narrow and fully verified, use the low-level `git write-tree` + `git commit-tree` + `git update-ref` fallback only under transactional closeout preconditions, then push and prove local/remote SHA equality in the same window. See `references/commit-tree-fallback-when-commit-hangs.md`.
24. If a tool-call/context limit arrives after staging files or creating a local ahead commit but before validation/commit/push/closure, produce an explicit staged-work handoff: say the issue is not closed, list staged paths and local ahead commits separately, report only last verified checks, and order the remaining transactional steps. Do not start the next repo from the handoff. See `references/tool-limit-staged-work-handoff.md`.
24. If final `git status --short` shows only `.fuse_hidden*` files under `.planning/quick/` while a provider/review process still has an open file handle, treat it as active-process residue rather than a durable artifact. Do not force-remove or commit it; prove `HEAD == origin/main`, no tracked diff, and report the placeholder/owner as a local checkout blocker. See `references/fuse-hidden-active-provider-closeout.md`.
25. If the live index is blocked by background `git status -z -uall` storms and even an isolated `GIT_INDEX_FILE` + `git read-tree` commit path hangs, do not leave an unpushed handoff. For a single-file docs/handoff emergency, build the commit tree directly with plumbing: `git hash-object -w <file>`, `git ls-tree` the affected parent trees, replace the one path with `git mktree`, `git commit-tree`, `git update-ref`, then push and repair the live index path with `git add <file>` after clearing any stale zero-byte `.git/index.lock`. Report broad status timeouts separately from remote sync proof.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
### `tool-limit-staged-work-handoff`

- Session reference: `references/tool-limit-staged-work-handoff.md`.
- Preserved insight: When tool/context budget expires after staging files or creating a local ahead commit but before transactional closeout, the final handoff must explicitly say the issue is not closed, separate staged paths from local commits, name only verified checks, and block starting the next repo until validation/commit/push/close/clean proof is complete.

### `fuse-hidden-active-provider-closeout`

- Session reference: `references/fuse-hidden-active-provider-closeout.md`.
- Preserved insight: During final commit/push closeout, `.fuse_hidden*` placeholders can remain when active provider review processes keep deleted prompt/output files open; verify remote sync and tracked cleanliness, but report the placeholder/owner as a local checkout blocker instead of force-removing or committing it.

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

### `live-branch-added-files-push-with-generated-churn`

- Session reference: `references/live-branch-added-files-push-with-generated-churn.md`.
- Preserved insight: When committing/pushing requested added files from a live workspace-hub branch, stage narrowly, verify exact remote files/commit, use audited pre-push bypass only for unrelated hook debt, and report fresh post-push `.claude/state` churn separately from remote push success.

### `concurrent-closeout-and-rebase-drift`

- Session reference: `references/concurrent-closeout-and-rebase-drift.md`.
- Preserved insight: Stale files/branches/worktrees accumulate when issue closure is separated from same-window push, branch/worktree disposition, and clean-state proof; when a foreign rebase disrupts a just-pushed closeout, report remote landed state separately from local checkout conflict state and do not abort/continue without approval.

### `subagent-assisted-rebase-recovery-closeout`

- Session reference: `references/subagent-assisted-rebase-recovery-closeout.md`.
- Preserved insight: Recover shared-root rebase drift by first dispatching a read-only subagent for ownership/reflog/PR-state evidence, then fast-forwarding only if the root is merely stale, writing the recovery log from a clean isolated worktree, pushing the docs-only commit, removing temporary branch/worktree, and proving clean sync.

### `git-hang-closeout-preservation`

- Session reference: `references/git-hang-closeout-preservation.md`.
- Preserved insight: When PRs are merged and branch heads are contained but local Git status/diff/worktree checks hang due concurrent Claude/Codex processes, preserve closeout evidence outside the repo and keep final ledger/cleanup pending; do not delete worktrees or claim clean sync from containment proof alone.

### `transactional-closeout-race-and-active-root-sessions`

- Session reference: `references/transactional-closeout-race-and-active-root-sessions.md`.
- Preserved insight: Treat post-closure stale files/branches/unmerged commits/worktrees as a workflow failure requiring RCA and transactional repair; push/merge proof, branch/worktree disposition, explicit preservation, ledger commit, and clean/synced proof belong in the same closeout window, while active root sessions block stashing/deletion of unowned dirt.

### `stale-git-config-lock-closeout-recovery`

- Session reference: `references/stale-git-config-lock-closeout-recovery.md`.
- Preserved insight: Recover stale `.git/config.lock` during closeout by holding the repo mutex, proving no active Git owner/rebase/index lock, preserving the lock file outside the repo, removing it under lock, and guarding zero-match process-count pipelines under `set -euo pipefail`.

### `active-root-closeout-blocker-bounded-probes`

- Session reference: `references/active-root-closeout-blocker-bounded-probes.md`.
- Preserved insight: When closeout state has synced remote but dirty live-owned root and broad Git commands hang, use bounded probes, remove only independently proven safe worktrees under lock, and report synced-vs-clean as separate truths; do not call the issue closeout complete.

### `root-session-wait-and-divergence-gate`

- Session reference: `references/root-session-wait-and-divergence-gate.md`.
- Preserved insight: Waiting for active root sessions requires process classification, not only a zero CWD count; if local auto-sync and remote session-signal commits diverge while root is dirty, inspect both sides and avoid live-root merge/rebase/stash until ownership is safe.

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
