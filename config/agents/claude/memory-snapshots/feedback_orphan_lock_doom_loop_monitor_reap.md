---
name: feedback_orphan_lock_doom_loop_monitor_reap
description: "Diagnosing/fixing a wedged parallel session — orphan .git/index.lock doom-loop, pgrep -x git vs -f detection, and monitor-reap unwedge"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c60d603d-e50b-48a4-96d2-e91e7b33970d
---

When a parallel session's reconcile dies mid-flight on `workspace-hub`, three coupled failure modes appear together; fix them in order: clear lock → reap monitors.

**1. Detect LIVE git with `pgrep -x git`, never `pgrep -f 'git …'`.** The session's bash `until`-loop monitors carry the literal text `git merge -X theirs` / `git push origin HEAD:main` / `git stash pop` in their command lines, so `pgrep -f 'git (merge|push|stash)'` matches the *monitor scripts*, not running git. This false-positive flipped my verdict twice and made a background watcher that polled `pgrep -f` unable to ever exit. `pgrep -x git` matches the executable (`comm=git`) only. Same trap as [[feedback_hermes_session_grep_journal_vs_active]] (grep-hit ≠ active use).

**2. Orphan `index.lock` doom-loop.** A dead reconcile leaves a stale `.git/index.lock`. Every retry `git merge` dies in ~3s with `fatal: Unable to create '.git/index.lock': File exists`; HEAD never advances, branch stays N-behind. Signature: lock mtime frozen hours old + `pgrep -x git`=0 + `MERGE_HEAD` absent. Fix: `rm .git/index.lock`, guarded — only if no `pgrep -x git` AND lock older than ~2min (`find .git/index.lock -mmin +2`); lock is owned by the user, no sudo. Companion to [[feedback_git_status_lock_storm]] and [[feedback_autostash_lock_race_workspace_hub]].

**3. Wedged session is foreground-blocked on a dead monitor.** A parked session shows `Sl+` (not crashed) with many bash `until`-loop children. Clearing the lock alone leaves a healthy-but-undriven repo. Reaping the orphaned monitors returns control and the session resumes itself (`Sl+`→`Rl+`) and re-drives its own merge — preferable to merging on its branch (race; see [[feedback_multi_agent_commit_serialization]]). Scope the kill precisely: match the dead session's unique `<session-id>/tasks` path, restrict to `comm=bash`, and explicitly exclude `pgrep -x claude` PIDs and `$$`. The auto-mode classifier will deny a composite kill that also targets other sessions' `git status` procs — those self-drain once monitors die, so kill monitors only.

**Why:** waiting on a "still running" parallel reconcile is futile when it's a doom-loop or a wedge — it cannot self-resolve. **How to apply:** verify with `pgrep -x git`; if a stale lock + idle/`Sl+` session, clear lock (guarded) then reap monitors (scoped); let the session finish its own push (`git push origin HEAD:main` is the repo's sync convention). Don't merge/push on its branch yourself unless the session is confirmed gone. Related: [[feedback_wait_for_safety_bg_task_before_destructive_op]], [[feedback_autosync_silent_pusher]].
