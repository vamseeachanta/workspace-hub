---
name: crossprovider hermes github-bulk-comment-throttle-match-submitted-too
description: GitHub bulk comment throttle: match 'submitted too quickly' error string
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, throttle-pattern, bulk-operations]
---

Batch commenting hits throttle with error 'was submitted too quickly' (not standard 'rate limit'). Threshold: ~500 posts on single token in ~25min. Solution: regex match the exact string, cap batches at ≤200, enforce 1hr cooldown between batches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
