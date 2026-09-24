---
name: crossprovider gemini structure-level-inventory-parity-after-migration
description: Structure-level inventory parity after migration
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [verification-strategy, file-integrity, inventory-checking]
---

Verify file-structure parity after migration using `find` with exclusions for pointer/README files, then path-normalize and diff. This is more robust than raw file counts, which mask orphaned or unexpectedly-named files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
