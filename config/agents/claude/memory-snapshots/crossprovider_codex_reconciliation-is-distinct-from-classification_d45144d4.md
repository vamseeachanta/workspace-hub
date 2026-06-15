---
name: crossprovider codex reconciliation-is-distinct-from-classification
description: Reconciliation is distinct from classification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-quality, reconciliation, issue-265]
---

Tagging 480 local files as unmatched without attempting to reconcile them against a candidate universe is silent data loss. Issue #265: all local PDFs were marked existing + unmatched, blocking future dedup/tracking. Must attempt matching when a public reference exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
