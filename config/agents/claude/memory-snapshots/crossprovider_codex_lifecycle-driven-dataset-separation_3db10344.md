---
name: crossprovider codex lifecycle-driven-dataset-separation
description: Lifecycle-driven dataset separation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [data-architecture, huggingface, dataset-design]
---

Datasets with distinct update cadences or schema evolution should live in separate HF projects (e.g., atlas-explorer for static lookups, runs-ledger for algorithm outputs, riser-database for new data). Mixing introduces coupling and breaks downstream automation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
