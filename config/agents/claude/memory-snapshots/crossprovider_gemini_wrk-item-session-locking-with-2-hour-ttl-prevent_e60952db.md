---
name: crossprovider gemini wrk-item-session-locking-with-2-hour-ttl-prevent
description: WRK item session locking with 2-hour TTL prevents concurrent execution collisions
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, workflow]
---

Add `locked_by` (session ID) and `locked_at` (ISO timestamp) fields to WRK frontmatter. Claim atomically (temp file + mv). Stale locks older than 2h auto-release with warning. Exit code 4 on collision, allowing caller to retry.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
