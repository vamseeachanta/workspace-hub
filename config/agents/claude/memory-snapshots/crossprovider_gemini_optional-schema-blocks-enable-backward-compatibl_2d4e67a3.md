---
name: crossprovider gemini optional-schema-blocks-enable-backward-compatibl
description: Optional schema blocks enable backward-compatible adoption
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [schema-design, backward-compatibility, incremental-adoption]
---

New schema fields marked optional (e.g., quality_signals block) prevent breaking legacy workflows. Validation degrades gracefully when new fields absent. Supports incremental rollout without author burden. WRK-667 pattern.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
