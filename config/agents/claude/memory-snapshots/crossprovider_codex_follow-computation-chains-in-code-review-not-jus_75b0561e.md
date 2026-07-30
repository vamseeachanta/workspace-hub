---
name: crossprovider codex follow-computation-chains-in-code-review-not-jus
description: Follow computation chains in code review, not just diffs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [review, correctness, tracing]
---

Reading a diff alone can miss bugs that emerge downstream. Trace call chains and state flow: verify no double-computation, check how cached/computed state propagates to callers, confirm no state splits or inconsistencies. One-off code inspection often hides problems visible only at integration points.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
