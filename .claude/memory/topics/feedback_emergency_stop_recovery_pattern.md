> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_emergency_stop_recovery_pattern.md

---
name: Emergency-stop recovery during destructive sweeps
description: When a destructive script's verification step reveals a problem AFTER kickoff, kill -P stops the next iteration in time; partial deletion is recoverable via parent-repo worktree registry
type: feedback
originSessionId: 73cbf578-6fb3-4436-9a95-06ed471cd8b1
---
When a sweep script verifies one thing then immediately deletes (and you discover the verify result was wrong AFTER the script started), `kill -P <parent-pid>` between iterations can stop the next entry from being processed. Sequential per-entry processing means each entry's deletion is atomic in that one operation — partial state is contained to the in-flight item.

Concrete recovery on 2026-05-01: `assetutilities-issue-2461` was classified ORPHAN (HEAD not reachable from origin/main), but the verify ran BEFORE `git fetch`, so `origin/main` was stale. The sweep then started; first item deleted (small, fast); second item (`assetutilities-issue-2461`) had its `.git` gitlink file deleted before kill-P caught the script. Working-tree files were still on disk.

**Recovery path** when a worktree-linked dir's `.git` gitlink is gone but content remains:
1. The parent repo's `.git/worktrees/<wt-name>/` registry entry usually still exists (gitlink deletion ≠ registry entry removal).
2. Inside that registry entry, `HEAD` file holds the SHA the worktree was at.
3. The branch name from the registry's `gitdir` references can be queried in the parent repo: `git -C <parent> branch --contains <SHA>` finds containing branches.
4. Push the branch from the parent: `git -C <parent> push --no-verify -u origin <branch>` — this preserves the work durably to remote, no need to repair the broken worktree.
5. Then `git -C <parent> worktree remove --force <broken-wt-path>` cleans up the broken state + its registry entry.

**How to apply:** structure destructive sweeps so the verify-and-act loop has a stop point per iteration (background script + monitorable progress log). When you see a verification result that shouldn't proceed, kill the parent pid first, THEN diagnose. The parent-repo registry is a load-bearing safety net for partial-delete recovery.

**Lesson on staleness:** `git ls-remote origin "refs/heads/<branch>"` reflects the remote NOW, but `merge-base --is-ancestor HEAD origin/main` uses the LOCAL refs/remotes/origin/main which can be stale. Always `git fetch origin` before ancestry verification, especially for "is this orphan" checks.
