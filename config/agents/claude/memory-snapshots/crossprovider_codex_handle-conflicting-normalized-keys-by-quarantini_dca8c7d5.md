---
name: crossprovider codex handle-conflicting-normalized-keys-by-quarantini
description: Handle conflicting normalized keys by quarantining and preserving lineage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-extraction, conflict-resolution, lineage]
---

When extraction discovers multiple rows that normalize to the same key but carry conflicting values, quarantine them explicitly (do not silently choose one). Preserve exact duplicates separately from conflicts. Expose only unambiguous keys in the lookup layer. Declare quarantine counts in the manifest.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
