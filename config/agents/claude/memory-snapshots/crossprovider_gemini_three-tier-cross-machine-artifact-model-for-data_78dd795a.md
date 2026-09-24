---
name: crossprovider gemini three-tier-cross-machine-artifact-model-for-data
description: Three-tier cross-machine artifact model for data governance
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-architecture, cross-machine, governance]
---

Tier 1 = git-tracked (authoritative), Tier 2 = shared mount /mnt/ace/ (preferred when reachable, written by ingest), Tier 3 = local cache (never authoritative, never written by core processes). Plans explicitly assign each artifact to a tier with authority/sync rules and test that Tier 3 is excluded.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
