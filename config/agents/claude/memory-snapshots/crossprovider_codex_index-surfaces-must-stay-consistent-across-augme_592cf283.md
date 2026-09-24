---
name: crossprovider codex index-surfaces-must-stay-consistent-across-augme
description: Index surfaces must stay consistent across augmentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, index, consistency, llm-wiki]
---

When updating a page and modifying main index.md and log.md, also update any paginated index surfaces (e.g., sources-index/sources-039.md, figure_inventory.csv in domain-specific paths). Stale surfaces leave inconsistent state that breaks downstream discovery and verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
