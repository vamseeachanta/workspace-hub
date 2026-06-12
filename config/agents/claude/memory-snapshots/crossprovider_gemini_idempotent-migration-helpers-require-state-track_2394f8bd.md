---
name: crossprovider gemini idempotent-migration-helpers-require-state-track
description: Idempotent migration helpers require state tracking and atomic file ops
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [idempotence, state-management, file-operations]
---

Migration scripts that move or rename large file sets must be re-runnable without duplication. Use state files (.state.json) to track progress and guard each operation with `test -f` checks. Atomic operations (move, not copy+delete) prevent partial states. Rerunning must produce identical output.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
