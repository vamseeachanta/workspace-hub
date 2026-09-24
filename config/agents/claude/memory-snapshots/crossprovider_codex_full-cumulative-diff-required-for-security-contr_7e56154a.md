---
name: crossprovider codex full-cumulative-diff-required-for-security-contr
description: Full cumulative diff required for security contract reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-scope, security-assessment]
---

Truncated or partial diffs prevent complete assessment of security contracts. Authority violations, transport edge cases, and state-mutation boundaries can only be verified when the entire flow is visible. A review on a partial diff must explicitly mark itself as incomplete or UNAVAILABLE rather than downgrade findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
