---
name: crossprovider codex enumerate-with-dedup-logic-causes-index-misalign
description: Enumerate with dedup logic causes index misalignment in mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [indexing-bugs, deduplication, list-comprehension]
---

Using enumerate(finditer(...)) to assign indices, then skipping duplicates during dedup, leaves later entries with shifted indices. This causes misaligned URL/data mappings (e.g., second unique rig mapped to third URL). Reassign indices after dedup, not before.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
