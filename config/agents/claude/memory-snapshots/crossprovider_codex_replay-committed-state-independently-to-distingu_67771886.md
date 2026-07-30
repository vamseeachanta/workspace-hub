---
name: crossprovider codex replay-committed-state-independently-to-distingu
description: Replay committed state independently to distinguish code bugs from environmental artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [testing, verification, process]
---

Working-tree state can be contaminated by parallel writers or tool-created residue. Verify by replaying RED archive from committed history and checking tree/history byte-equivalence before approval; contaminated worktree failures are not evidence of code correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
