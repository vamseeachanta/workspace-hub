---
name: crossprovider gemini wave-based-spec-migration-prevents-catastrophic-
description: Wave-based spec migration prevents catastrophic failure on large corpora
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, governance, batch-processing]
---

Large corpus migrations (digitalmodel: 5543 files) fail as single-shot operations due to I/O contention and collision detection overhead. Split by repository, batch by subtree, and verify idempotency after each wave. Fail-fast on target collision in wave-1 (no overwrite).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
