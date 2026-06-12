---
name: crossprovider gemini fallback-and-cache-strategy-for-remote-sources
description: Fallback-and-cache strategy for remote sources
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [resilience, distributed-systems, degradation]
---

When a remote/mounted source becomes unavailable, degrade gracefully: use indexed metadata and cached summaries rather than blindly re-downloading duplicates. Record source_unavailable state in the resource pack and continue. Prevents cascading retries and wasted I/O on transient mount failures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
