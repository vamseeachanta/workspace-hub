> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_bulk_comment_cumulative_volume_threshold.md

---
name: feedback_bulk_comment_cumulative_volume_threshold
description: "GitHub addComment secondary rate-limit is cumulative-volume-aware, not just rate-aware — ~500 posts on a single token in ~25min trips it even at 30/min pacing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b5c609c4-cd38-41a6-9044-510a56899eb8
---

GitHub's documented secondary rate-limit for content-creation actions is often described as ~30 mutations/min. In practice for `addComment` mutations from a single authenticated token, there is ALSO a per-token cumulative-volume ceiling that triggers throttling around **500 posts in ~25 minutes**, regardless of how steady the per-minute rate is.

**Why:** verified empirically on 2026-05-18 during workspace-hub bulk-comment run. Pacing was 2s sleep + ~0.86s gh API latency = ~21 posts/min, well under the documented 30/min ceiling. First 494 posts succeeded cleanly. At post #495 throttling began and continued unbroken for the remaining 382 posts in the run. Per-minute rate never spiked. The trigger was cumulative volume, not instantaneous rate.

**How to apply:** when planning a bulk `gh issue comment` / `gh pr comment` / `gh discussion comment` run that targets more than ~400 items on a single token, choose ONE of these strategies:

1. **Batch with cooldowns:** split into ≤200-item batches with 1hr cooldown between batches. Total wall-time stretches, but each batch lands cleanly.
2. **Increase pacing to ~6-10s/comment:** roughly halves the cumulative ceiling pressure. Empirically untested but consistent with GitHub's published guidance to "wait a few seconds between writes" being a floor, not a ceiling.
3. **Split tokens across multiple machine identities:** if the work is partitionable, dispatch from 2-3 machines (each with its own token) so the per-token cumulative budget resets independently. Pairs with [[feedback_cross_machine_execution]].
4. **Avoid bulk-comment entirely for >400 targets:** ask whether the same outcome can be achieved with a single repo-level discussion thread, a pinned issue, or a project-board annotation, instead of N per-issue comments.

Estimated cooldown for a tripped per-token ceiling: **~1-2 hours** before retries succeed (untested empirically as of 2026-05-18 — first observation).

**Pair with [[feedback_github_addcomment_submitted_too_quickly]]:** the throttle response string is the detection signal; this memory is about prevention via planning.

**Related:** [[feedback_github_addcomment_submitted_too_quickly]], [[feedback_parallel_gh_issue_create_reverses_numbers]], [[feedback_check_parallel_work]].
