> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_check_issue_state_before_implementing_on_detached_head.md

---
name: feedback_check_issue_state_before_implementing_on_detached_head
description: "Before coding an issue, branch from origin/main and confirm it isn't already closed/PR-merged by a parallel session — detached-HEAD sessions silently produce stale-base work"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 97f5bdec-e4ac-46ef-9621-afbf4c40dc6c
---

On 2026-06-09 I created #2992 (statusline weekly-reset countdown), implemented it (TDD, 4 bats green), committed, and opened PR #3005 — only to discover a **parallel session had already implemented the identical feature, merged it via #3004 (11:35Z), and closed #2992** with a *better* version (Python `resets_at` parser, `source`-aware skip for unavailable AND estimated, more tests). All my implementation effort was wasted.

Two compounding root causes:
1. The session started on a **detached HEAD** (`git status` showed `Current branch: HEAD`). I ran `git checkout -b feat/... ` off it, so my branch base was 154–159 commits behind origin/main. The PR diff ballooned to 100 files / +500k lines (the drift between the ancient merge-base and current main), not my 2-file change — the classic stale-base hazard from [[feedback_recover_stale_branch_for_pr]].
2. I did NOT verify the issue's live state on the remote before implementing — violating [[feedback_check_parallel_work]]. A 10-second `gh pr list --search "<issue#> in:title" --state all` + `gh issue view <#> --json state` would have shown the merged PR and CLOSED issue before I wrote a line.

**Why:** the ecosystem runs multiple concurrent sessions/agents against the same GitHub-issue backlog; auto-sync keeps local main drifting. Detached-HEAD + no pre-flight state check = guaranteed duplicate or stale-base work.

**How to apply:** Before implementing ANY issue, FIRST: (a) `git fetch origin` and branch explicitly from `origin/main` (`git checkout -b <branch> origin/main`), never from a detached/ambient HEAD; (b) check the issue is still OPEN and has no merged/open PR (`gh issue view <#> --json state,stateReason`; `gh pr list --search "<#> in:title" --state all`). If closed/merged: stop, clean up, report — don't re-implement. When cleaning up redundant work, `git reset --hard` on cron-churn the agent didn't author is auto-denied — use targeted `git checkout --ours -- <files>` (stash is retained on pop-conflict, so data is safe).
