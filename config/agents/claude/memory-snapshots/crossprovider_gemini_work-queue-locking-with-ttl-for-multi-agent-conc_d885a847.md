---
name: crossprovider gemini work-queue-locking-with-ttl-for-multi-agent-conc
description: Work-queue locking with TTL for multi-agent concurrency
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [work-queue, concurrency, multi-agent]
---

WRK items can be session-locked with auto-expiry (default 7200s) to prevent concurrent modification by multiple agents. When a lock exceeds TTL, it is reclaimed with a warning. Frontmatter stores locked_by session ID and locked_at timestamp. Essential for orchestrated multi-agent work on shared issue queues.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
