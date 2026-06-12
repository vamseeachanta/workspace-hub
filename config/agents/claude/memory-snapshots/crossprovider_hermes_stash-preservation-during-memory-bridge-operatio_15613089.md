---
name: crossprovider hermes stash-preservation-during-memory-bridge-operatio
description: Stash preservation during memory bridge operation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-bridge, git-operations, workspace-hub]
---

When recovering from pre-bridge-stash after a failed bridge commit, preserve non-memory tracked files that were stashed alongside memory files. Only drop stash after verifying all preserved content is outside the intended bridge scope (e.g., logs/orchestrator/ files). This prevents silent data loss.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
