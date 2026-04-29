> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_autosync_silent_pusher.md

---
name: Auto-sync as silent pusher (resolves contention, doesn't only cause it)
description: Workspace-hub's auto-sync also pushes local-ahead commits when its window opens — a `[rejected]` push from your shell may already have been resolved by auto-sync seconds later
type: feedback
originSessionId: 68238359-8235-44a3-bdd9-b90342e2bd73
---
Existing memory frames auto-sync as the source of races (`feedback_merge_race_silent_revert`, `feedback_multi_agent_commit_serialization`, `feedback_retry_loop_reset_hazard`). It also has a counter-pattern: auto-sync detects local-ahead-of-origin states and pushes when it gets a clean window. Observed in 2026-04-24 contention sequence: ran `git commit` for a docs handoff prompt → `git push origin main` rejected as non-fast-forward → ran `git rebase origin/main` (which produced its own confusing lock errors but actually completed per reflog) → minutes later `git status` showed local main equals origin/main with no explicit re-push from me. The rebased commits had reached origin via auto-sync's own push cycle.

**Why:** Auto-sync's job is to keep local and origin in sync in *both* directions. When it sees local-ahead, it pushes — using its own retry/lock-handling logic that often succeeds where a foreground shell push hits transient rejection. This is the "well-behaved counterpart" to the contention pattern: same daemon, different polarity.

**How to apply:**
- After any `[rejected]` push, *don't immediately retry*. Wait 1–5 minutes, then run `git fetch origin <branch>` and `git status -uno --short --branch`. If divergence is zero, auto-sync resolved it for you and a manual retry would be a no-op or a duplicate.
- This composes with `feedback_reflog_as_ground_truth`: a "failed" push followed by an apparent rebase failure can together mask a fully-successful end state. Always check post-operation reality before manual recovery.
- When you actually do need to push manually after a rejection, use `git pull --rebase origin <branch>` first so your commits land on top of whatever auto-sync (or another session) just pulled in. Use `--autostash` if the working tree has session-state mods (`.recent_edits` etc.) — though note a hook may intercept and rename the autostash to `foreign-session-<timestamp>`.
- Don't engineer push retry loops — auto-sync is a parallel push consumer, and competing with it can produce the merge-race silent revert pattern. The right primitive is wait-then-verify, not retry-on-failure.
