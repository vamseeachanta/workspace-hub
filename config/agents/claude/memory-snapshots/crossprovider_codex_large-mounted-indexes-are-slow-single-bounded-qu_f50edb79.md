---
name: crossprovider codex large-mounted-indexes-are-slow-single-bounded-qu
description: Large mounted indexes are slow; single bounded query is better than re-running
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [tooling, performance, research]
---

Drive-index queries on mounted filesystems timeout after 60–90 seconds per query. Polling or re-running the same query wastes time. Run once with hard timeout; if incomplete, report lower bounds and coverage gaps explicitly rather than claiming zero evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
