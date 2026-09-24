---
name: crossprovider codex manifest-expansion-preserves-originals-nests-exp
description: Manifest expansion preserves originals, nests expanded records
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-structures, inventory, test-first, backup-pattern]
---

When expanding a metadata manifest (e.g., directory-level inventory to file-level), preserve the original parent records unchanged, nest or reference file entries with backward pointers, backup the original before writing, and test the expansion rules before running against live data. Verify total counts and category breakdowns afterward.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
