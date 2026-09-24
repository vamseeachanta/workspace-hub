---
name: crossprovider codex aggregate-stats-registries-are-not-joinable-inve
description: Aggregate-stats registries are not joinable inventories
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-model, inventory, input-specification]
---

A registry containing only `{total_docs, by_source_counts, by_domain_counts}` is not a per-record source inventory. If plan requires per-document join but only aggregate stats available, that's an input-sufficiency gap, not graceful degradation. Require the per-record corpus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
