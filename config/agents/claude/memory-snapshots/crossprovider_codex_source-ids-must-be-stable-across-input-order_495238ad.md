---
name: crossprovider codex source-ids-must-be-stable-across-input-order
description: Source IDs must be stable across input order
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-disposition, inventory, determinism]
---

When discovering multiple root paths for inventory/recommendation systems, derive source IDs from canonicalized sorted paths, not caller input order. Non-deterministic IDs prevent reproducible cross-session recommendations and make peer-matching unreliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
