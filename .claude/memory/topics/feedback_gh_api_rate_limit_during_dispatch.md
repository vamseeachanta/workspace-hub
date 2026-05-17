> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-17
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_gh_api_rate_limit_during_dispatch.md

---
name: gh-api-rate-limit-during-dispatch
description: "GitHub GraphQL API limits to 5,000/hr per user. Batch dispatches of issues + comments + cross-refs hit this fast. Watch quota proactively when creating 10+ issues in a session."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37c4fd1d-3784-4903-a5ea-5fe997dd7044
---

**Don't burn the 5K/hr GraphQL quota in a single dispatch wave.**

**Why:** 2026-05-12 Domain Knowledge Sweep dispatch hit the limit after creating 14 issues + ~8 cross-ref comments in ~30 minutes. Parallel sessions (codex-openai-codex plugin doing cross-review work on #2675) shared the quota. Resulted in mid-dispatch failure when posting findings from preliminary R5 audits. Local commits had to be parked while waiting 28 minutes for reset.

**How to apply:**
1. Before any dispatch creating 10+ issues, run `gh api rate_limit --jq '.resources.graphql'` to check budget
2. Batch issue creation in waves of 5-7, not all at once
3. Prefer fewer rich-body posts over many small comments (one comment with 5 cross-refs ≪ five separate comments)
4. When you hit rate limit mid-dispatch:
   - Don't retry-in-a-loop (poll burns more quota)
   - Save pending posts to `docs/sessions/<date>-pending-gh-posts.md`
   - Use `ScheduleWakeup` to retry after reset
   - Local commits don't need GitHub — keep doing those
5. If parallel sessions are active (check `pgrep -af 'claude\|codex\|hermes'`), assume the quota is partially burned already
6. GraphQL and core REST quotas are separate (`gh api rate_limit --jq '.resources'`); `gh issue` uses GraphQL, simple `gh api repos/.../issues/N` uses core

**Recovery pattern:**
- `date -d @<reset_epoch> +"%H:%M:%S %Z"` to compute reset time
- Schedule wakeup for reset + 60s buffer
- Replay pending posts in order
