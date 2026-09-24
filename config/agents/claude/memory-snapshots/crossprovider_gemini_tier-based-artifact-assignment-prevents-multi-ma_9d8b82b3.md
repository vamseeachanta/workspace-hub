---
name: crossprovider gemini tier-based-artifact-assignment-prevents-multi-ma
description: Tier-based artifact assignment prevents multi-machine ambiguity
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, distributed-systems, clarity]
---

Use explicit tier classification for artifacts: T1 (authoritative git-tracked), T2 (preferred when reachable, e.g., /mnt/ace paths), T3 (local-only, ephemeral). This clarifies canonical locations and resume behavior in distributed setups.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
