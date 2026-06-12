---
name: crossprovider hermes cross-reference-count-divergence-signals-freshne
description: Cross-reference count divergence signals freshness or deduplication bugs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-quality, aggregation, debugging]
---

Resource count mismatch (247 vs 248) indicated stale caching or duplicate aggregation. Log per-source counts separately; audit deduplication logic when counts diverge; never assume aggregated totals are fresh.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
