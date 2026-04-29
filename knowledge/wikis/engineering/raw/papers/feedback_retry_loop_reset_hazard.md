> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_retry_loop_reset_hazard.md

---
name: Retry-loops with `git reset` can strip staged edits under auto-sync contention
description: Chaining `git reset HEAD -- . && git add X && git commit` in a retry loop against concurrent auto-sync can land commits with your message but unrelated content
type: feedback
originSessionId: f5aefbf6-482d-404e-84f9-d1ebc70e92a3
---
When the git index is contested (auto-sync cron running concurrently, parallel merges, stash applies), a naïve retry pattern like:

```bash
for i in 1..10; do
  while [[ -f .git/index.lock ]]; do sleep 1; done
  git reset HEAD -- . && git add X Y && git commit -m "..."
done
```

has a correctness hazard: between your `git add` and `git commit`, another process can win the lock, run its own reset/checkout, and restore your target files to HEAD before your commit captures them. Or — as happened on 2026-04-19 — your own `git reset` strips a concurrent change that was staged, and your commit lands with your message but carrying an unrelated diff that another process added in between.

**Why:** The retry loop treats "lock-free" as "index-quiet." That's false under concurrent writers. Lock acquisition is necessary but not sufficient for staged-content-is-what-I-intended.

**How to apply:**
1. **Cheapest fix:** After `git add`, capture `git diff --cached` and compare against an expected-files list before `git commit`. If it doesn't match, abort and re-stage.
2. **Better fix:** Do docs-only and cosmetic commits in a dedicated worktree — its index is independent of main's, so auto-sync contention can't intrude.
3. **If a mislabeled commit lands:** do NOT force-push amend (nonlocal effects: CI re-runs, reviewer confusion). Add a follow-up commit that reapplies the intended changes and explains the mislabel. Git history truth-in-advertising beats history tidiness.

Context: Session 2026-04-19, commits `9f931bcdb` (mislabel) and `f2a4b9b5f` (clarifying follow-up).
