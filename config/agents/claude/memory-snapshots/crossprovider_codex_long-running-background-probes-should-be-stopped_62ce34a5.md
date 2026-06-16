---
name: crossprovider codex long-running-background-probes-should-be-stopped
description: Long-running background probes should be stopped and replaced
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [background-work, timeouts, search-optimization]
---

Broad searches (find, grep, rg) that exceed useful runtime (>5 min) should be killed and replaced with targeted queries. Do not let stalled background work block task closeout. Save output of completed probes; do not wait indefinitely for stragglers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
