---
name: crossprovider gemini mounted-source-registry-pattern-for-distributed-
description: Mounted-source registry pattern for distributed resources
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, distributed-systems, data-sourcing, resource-management]
---

Record mount points, auth posture, cached evidence TTL, and degradation rules in a structured registry. When remote mounts become unavailable, fall back to indexed metadata and cached summaries rather than attempting blind downloads—this avoids redundant data pulls and graceful degrades planning quality instead of breaking entirely.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
