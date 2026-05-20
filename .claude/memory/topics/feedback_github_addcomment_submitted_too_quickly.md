> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_github_addcomment_submitted_too_quickly.md

---
name: feedback_github_addcomment_submitted_too_quickly
description: "GitHub addComment GraphQL throttle returns literal \"was submitted too quickly\" — not \"rate limit\"; rate-limit detection regex must include this exact phrase"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b5c609c4-cd38-41a6-9044-510a56899eb8
---

When `gh issue comment` (or any `addComment` GraphQL mutation) is throttled by GitHub's secondary rate-limit, the returned error string is:

```
GraphQL: was submitted too quickly (addComment)
```

It does NOT contain `"rate limit"`, `"abuse"`, `"secondary rate"`, or `"wait a few minutes"` — the four phrases that normally signal throttling in REST API responses. A backoff scanner built for the REST patterns will silently miss every throttle event.

**Why:** verified empirically on 2026-05-18 during workspace-hub bulk-comment run (876 targets, [[feedback_bulk_comment_cumulative_volume_threshold]]). Script plowed through 382 guaranteed-failing requests after first throttle at request #495 because the regex `("rate limit"|"abuse"|"secondary rate"|"wait a few minutes")` matched none of them. 0 backoff events fired across 382 failures. Pure wasted API budget.

**How to apply:** when writing throttle-detection for any code path that calls `gh issue comment`, `gh pr comment`, `gh pr review --body`, `gh discussion comment`, or any other `addComment`-family mutation (including direct `gh api graphql` calls invoking `addComment`), include `"submitted too quickly"` in the throttle-pattern union. Compose pattern as: `("rate limit"|"abuse"|"secondary rate"|"wait a few minutes"|"submitted too quickly")`. On match, sleep at least 60s — and consider exiting early after 2-3 consecutive throttles, because the per-token cumulative ceiling per [[feedback_bulk_comment_cumulative_volume_threshold]] may need an hour to reset.

**Related:** [[feedback_bulk_comment_cumulative_volume_threshold]], [[feedback_parallel_gh_issue_create_reverses_numbers]] (different concurrency hazard, same gh CLI surface).
