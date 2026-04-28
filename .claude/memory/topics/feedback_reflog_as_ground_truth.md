> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_reflog_as_ground_truth.md

---
name: Reflog as ground truth during git operations
description: When in-flight git output suggests failure (lock errors, [rejected] push, mid-rebase staged-AD entries), check reflog and `git status` before retrying — the operation may have actually succeeded
type: feedback
originSessionId: 68238359-8235-44a3-bdd9-b90342e2bd73
---
Under workspace-hub's aggressive auto-sync, several git operations produce output that *looks* like failure but actually succeeded. Examples observed in one resolution sequence: (a) `git push origin main` printed `! [rejected] main -> main (fetch first)` — but inspection minutes later showed local main equals origin/main, so something pushed; (b) `git rebase origin/main` failed with `Unable to create '.git/index.lock': File exists` and "could not detach HEAD" — but the reflog showed the rebase did complete (HEAD@{N..0} traced through pick steps and "rebase finish, returning to refs/heads/<branch>"); (c) `git status` mid-rebase showed `AD` (added-in-index, deleted-in-tree) entries that I read as another session staging the same file — these were actually mid-rebase pick state, not racing-session pollution.

**Why:** Lock contention plus auto-sync plus background hooks means git commands sometimes report transient errors during retries that ultimately succeed, or print misleading status snapshots during multi-step operations like rebase. The intermediate stderr is not the source of truth — the reflog and the post-operation `git status` are.

**How to apply:**
- After any git operation that prints a lock error, `[rejected]`, or unexpected `AD`/`MM` index entries, *do not retry or recover yet*. First run: `git reflog HEAD -10`, `git rev-parse HEAD`, `git status -uno --short --branch`, `git fetch origin <branch>`. Compare reality to the apparent failure.
- Reflog entries during rebase show every `pick` step. If the chain ends at `(finish): returning to refs/heads/<branch>`, the rebase succeeded regardless of intermediate stderr.
- For `[rejected]` pushes, check `git status --branch` for ahead/behind markers. Zero divergence means something pushed (often auto-sync — see `feedback_autosync_silent_pusher`).
- During an active rebase, `AD` entries in `git status` can be normal pick-step bookkeeping, not external racing. Confirm by checking `git rev-parse --git-dir`/rebase-merge or rebase-apply directories before assuming pollution.
- Save the actual SHA before retrying anything destructive. If reflog confirms success, what looked like a failure was a redundant operation that's already done.
