---
name: crossprovider codex enrichment-fixes-must-guard-against-downstream-r
description: Enrichment fixes must guard against downstream re-runs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-pipelines, enrichment, durability, multi-phase]
---

When enriching tracked artifacts (e.g., adding schema fields to index records), later phases that rewrite the same file can clobber new fields. Approval requires evidence that all downstream re-run paths either preserve enriched data or are guarded to skip clobbering.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
