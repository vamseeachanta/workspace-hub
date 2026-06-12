---
name: crossprovider gemini safe-ecosystem-migration-protocol
description: Safe ecosystem migration protocol
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-integrity, migration, governance]
---

For large-scale file moves: dry-run manifest → user approval gate → apply with pre-collision detection → post-migration parity verification (sha256sum + path-normalized comparison). Prevents silent data loss and enables rollback if integrity checks fail.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
