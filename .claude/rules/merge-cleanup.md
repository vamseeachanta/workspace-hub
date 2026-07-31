# Merge cleanup — a merge is not done until its branch and worktree are gone

**When to apply:** every merge to `main`, in any repo of the ecosystem — whether the agent verified it and handed the human the command, or the human ran it. Also at session close, as a sweep.

**Why:** cleanup deferred is cleanup never done, and the residue is not inert. Measured on `ace-linux-1`, 2026-07-30: **44 remote branches already merged into `origin/main`**, and **17 git worktrees**, two of them holding branches that merged weeks earlier. Three of the 44 were merged in that same session and left behind — the debt accrues fastest from the person who best knows the branch is dead.

The cost is not disk. It is that a stale branch is indistinguishable from an in-flight one, so every later "is this work landed?" question needs a full investigation. This session spent real effort on exactly that: four "lost work" reports that turned out to be squash-merge artifacts, plus one genuine unpushed branch hiding among them. A clean branch list makes the real signal visible.

**How to apply:**

1. **Merge with `--delete-branch`.** `gh pr merge <N> --squash --delete-branch` removes the remote branch atomically. This is the default; the exceptions below are the only reasons to skip it.
2. **Then remove the local branch and any worktree** — `--delete-branch` does neither. `git worktree remove <path>` first (a branch checked out in a worktree cannot be deleted), then `git branch -d <name>`.
3. **Sweep periodically**, because step 1 gets skipped:
   ```bash
   git fetch --prune
   git branch -r --merged origin/main | grep -v 'origin/main\|HEAD'   # candidates
   git worktree list                                                   # stale checkouts
   ```
4. **`--merged` UNDER-reports — never treat its silence as "still in flight."** It tests ancestry, and **squash-merge rewrites SHAs**, so a squash-merged branch is *not* an ancestor of `main` and will not appear. Everything it lists is safe to delete; everything it omits still needs a content check (`git cat-file -e origin/main:<path>`, or the PR's merged state). See `reference_squash_merge_reachability_false_orphan`.
5. **Check open PRs before deleting anything.** A branch can be merged into `main` and still be the base of an open stacked PR. Deleting it **auto-closes that child** — see `feedback_delete_branch_closes_stacked_child_pr`.
6. **Never remove a worktree without inspecting it first.** `git status --porcelain` and `git ls-files --others --exclude-standard`. If anything is uncommitted, **archive it before `--force`**. Today's sweep found an untracked `genesis_launcher_args.py` in a merged worktree; it turned out to be an earlier draft superseded by a fuller version on `main`, but that was established by **diffing**, not assumed. Cleanup that destroys unreviewed work is worse than the mess it removes.
7. **Locked worktrees are opt-outs — respect them.** `git worktree list` marks them `locked`; someone locked it deliberately.

**Do NOT apply when:**

- The branch is the base of an **open PR** (stacked work) — merge and delete the child first, per `feedback_squash_merge_breaks_stacked_prs`.
- The worktree is **locked**, or holds uncommitted work you have not archived and reviewed.
- The branch carries commits **not** on `main` — verify by content before concluding it is stale (`feedback_narrow_grep_false_dead_before_deletion`).

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose now → Level 2 script `scripts/operations/merge-cleanup-sweep.sh` reporting merged-but-undeleted branches and stale worktrees, dry-run by default, refusing to touch dirty or locked worktrees. Promote once it has run clean a few times.

**Related:** [`merge-authorization.md`](merge-authorization.md) (who may run the merge — this rule governs what follows it), [`patterns.md`](patterns.md). Memory: `feedback_delete_branch_closes_stacked_child_pr`, `feedback_squash_merge_breaks_stacked_prs`, `reference_squash_merge_reachability_false_orphan`, `feedback_keep_data_at_fingertips` (delete only regenerable cruft).
