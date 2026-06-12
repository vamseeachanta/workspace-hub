---
name: crossprovider codex corpus-index-reconciliation-gate-required-for-mu
description: Corpus index reconciliation gate required for multi-source ingests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [data-integrity, corpus-ingest, reconciliation]
---

When multiple authoritative sources (e.g., JSONL registry, YAML catalog, on-disk inventory) claim counts for the same data, they diverge due to schema/scope differences (e.g., conference-index.jsonl: 27,735 vs catalog.yaml: 38,526 vs user's stated 19,797). Reconciliation is a blocking gate before any ingest phase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
