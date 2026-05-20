> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_git_status_lock_storm.md

---
name: Git status lock storm from Claude subagents
description: Long Claude sessions accumulate 10+ zombie `git status -z -uall` processes that block `git commit` for hours. `GIT_OPTIONAL_LOCKS=0` bypasses the status hook and unblocks commits.
type: feedback
originSessionId: 942f20e5-0933-4d14-9c8a-0fa2f91d5be7
---
In long-running Claude Code sessions, periodic `git status -z -uall` calls from Claude subagents (PPID = parent claude process) can accumulate over hours. Verified 2026-05-11: 10+ git status processes from a single claude PPID had been running for 2-3 hours each, blocking new `git commit` attempts with `Unable to create '.git/index.lock'`.

**Why:** Claude Code subagents poll repo state for status-line updates, branch awareness, or hooks. When the polling races with another git operation on a slow disk or under contention, the polling git status hangs holding `index.lock`. Killed instances respawn quickly (parent process keeps spawning).

**How to apply:**

1. **First diagnostic:** `pgrep -af "git status" | head -5` — if 5+ are running, you have a storm.
2. **Don't kill them naively** — the parent claude process respawns them. Killing the parent would terminate Claude itself.
3. **The fix:** prefix git commands with `GIT_OPTIONAL_LOCKS=0` to disable the index-lock acquisition for read-only ops:

   ```bash
   GIT_OPTIONAL_LOCKS=0 git status
   GIT_OPTIONAL_LOCKS=0 git log
   GIT_OPTIONAL_LOCKS=0 git diff
   ```

   This makes status/log/diff non-locking, ending the storm contribution.
4. **For your own commit:** also use `GIT_OPTIONAL_LOCKS=0 git commit` to skip the read-side lock probing in pre-commit. Your commit's write lock still applies normally.
5. **Cleanup:** If the storm has truly locked you out, `rm -f .git/index.lock` once you've verified no real owner (`fuser .git/index.lock` returns empty).

**Symptom timeline that triggers this:**
- 30+ minute sessions with lots of file edits and intermediate git operations
- Periodic Claude state-line refresh / hook fire
- The bash tool starts queuing or failing on git commands
- Background bash tasks that include `git status` start piling up unfinished

**Don't:** Spawn more parallel git commands when you see contention. They join the queue.
