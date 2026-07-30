---
name: crossprovider codex explicit-source-data-availability-matrix-for-ons
description: Explicit source data availability matrix for onshore expansion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [architecture, data-sourcing, onshore-pipeline]
---

Onshore lifecycle data is partial (RRC provides production/permits but not well-path/casing from public bulk dumps); be explicit about gaps rather than promise 'complete lifecycle'. Fast access layers (PatchOps) useful for testing; durability requires `/mnt/ace` materialization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
