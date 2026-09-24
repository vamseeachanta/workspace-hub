---
name: crossprovider gemini batch-subprocess-calls-and-cache-results-at-scal
description: Batch subprocess calls and cache results at scale
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [performance, subprocess, caching, scale]
---

Per-file subprocess calls (especially `git log`) become prohibitively expensive at scale (22K+ symbols). Execute once, cache results in memory, then do O(1) lookups during iteration. Applies to any operation that would execute the same external command 100+ times in a loop.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
