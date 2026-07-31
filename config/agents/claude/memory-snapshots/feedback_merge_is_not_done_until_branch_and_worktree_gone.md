---
name: feedback-merge-is-not-done-until-branch-and-worktree-gone
description: "Every merge to main must be paired with deleting the remote branch, the local branch, and the worktree — and `git branch --merged` under-reports because squash rewrites SHAs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a873f663-bb0d-4ae1-9209-add92b7b1a13
  modified: 2026-07-31T02:34:49.803Z
---

Owner directive 2026-07-30: **"merge to main should always be associated with delete stale branches, work trees etc."**

**Why:** cleanup deferred is cleanup never done. Measured on ace-linux-1 that day: **44 remote branches already merged into `origin/main`**, **17 worktrees** (two holding branches merged weeks earlier). Three of the 44 were merged in that same session and left behind — the debt accrues fastest from whoever best knows the branch is dead.

The cost is not disk. A stale branch is **indistinguishable from an in-flight one**, so every later "did this land?" needs a full investigation. That session burned real effort on exactly that: four false "lost work" reports that were squash-merge artifacts, with one genuine unpushed branch hiding among them.

**How to apply:**

1. `gh pr merge <N> --squash --delete-branch` — kills the remote branch atomically.
2. `--delete-branch` does **not** touch the local branch or worktree. `git worktree remove <path>` first (a branch checked out in a worktree cannot be deleted), then `git branch -d`.
3. Sweep periodically: `git fetch --prune`, `git branch -r --merged origin/main`, `git worktree list`.
4. **`--merged` UNDER-reports.** It tests ancestry; squash-merge rewrites SHAs, so squash-merged branches never appear. What it lists is safe to delete — **its silence proves nothing**. Verify omissions by content. See [[reference_squash_merge_reachability_false_orphan]].
5. **Never remove a worktree without checking `git status --porcelain` and `git ls-files --others --exclude-standard`.** Archive anything uncommitted before `--force`. The 2026-07-30 sweep found an untracked draft in a merged worktree; it was safely superseded, but that was established by diffing, not assumed.
6. Respect `locked` worktrees — a lock is a deliberate opt-out.
7. Do not delete a branch that is the base of an open stacked PR — it auto-closes the child. See [[feedback_delete_branch_closes_stacked_child_pr]], [[feedback_squash_merge_breaks_stacked_prs]].
8. **A branch with no upstream AND `rev-list --count origin/main..<branch>` > 0 exists only on this disk.** Never delete it — `git push -u origin <branch>` to rescue it, then it becomes an ordinary merge decision. The 2026-07-30 fleet sweep found 25 such branches across 8 repos (worst: digitalmodel `chore/1565-external-work-root-step4-tdd`, 40 commits; worldenergydata `backup/stale-main-pre-reorg-20260626`, 206).
9. **`[gone]` is only meaningful in a full-refspec clone.** In a single-branch clone (`fetch =
   +refs/heads/main:refs/remotes/origin/main` — gpu-claw's `assetutilities`, `llm-wiki-mkt-a`,
   `raw-to-knowledge-playbook`) a deleted upstream can never appear as `[gone]`, because non-main
   upstreams were never fetched. It fails toward danger: the branch reads as local-only, which
   triggers a needless rescue push. Check `git config --get-all remote.origin.fetch` first, and in
   restricted clones ask the server with `git ls-remote --heads origin <branch>` instead.
10. **Scope the sweep away from live refs.** Before a fleet-wide pass, list what a parallel session is pushing (`gh pr list --json updatedAt`, worktree mtimes) and put those branches/worktrees on an explicit protected list. Deleting under a running session is the one failure mode this rule can cause that it cannot undo.

Codified as `.claude/rules/merge-cleanup.md` (workspace-hub PR #3719). Governs what follows a merge; [[feedback_agent_can_verify_but_not_self_merge_pr]] governs who may run it.
