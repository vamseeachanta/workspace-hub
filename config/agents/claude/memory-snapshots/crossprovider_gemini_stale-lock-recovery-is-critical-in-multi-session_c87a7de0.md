---
name: crossprovider gemini stale-lock-recovery-is-critical-in-multi-session
description: Stale lock recovery is critical in multi-session environments
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, work-queue, session-management]
---

Work queue items locked by crashed sessions need automatic release after 2-3 hours. Without recovery, one defunct session blocks all others indefinitely. Use session state to discriminate live vs. dead lock holders; dead locks auto-release with stderr warning.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
