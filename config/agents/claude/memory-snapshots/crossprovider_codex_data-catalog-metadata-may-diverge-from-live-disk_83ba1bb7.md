---
name: crossprovider codex data-catalog-metadata-may-diverge-from-live-disk
description: Data catalog metadata may diverge from live disk state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, freshness, catalog-audit]
---

When auditing a data repository to propose it as a service surface, catalog entries (row counts, dataset sizes) can disagree significantly with live filesystem measurements (`du -sh`). Always validate freshness and reconcile discrepancies before recommending a data surface for agent consumption. Example: worldenergydata catalog claimed multi-GB totals while disk showed 391M.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
