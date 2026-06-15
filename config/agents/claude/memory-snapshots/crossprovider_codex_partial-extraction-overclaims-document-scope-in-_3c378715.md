---
name: crossprovider codex partial-extraction-overclaims-document-scope-in-
description: Partial extraction overclaims document scope in inventory
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, sigtto-extraction, data-quality]
---

HMSF/SIGTTO pattern: if ANY table extracted from a document, entire document marked `structured-table-csv` even if 3 of 6 candidates remain unprocessed. Inventory and manifest records false completion, hiding remaining extraction work. Fix: use `structured-table-partial-csv` when < 100% extraction, audit inventory completeness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
