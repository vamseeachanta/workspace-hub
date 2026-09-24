---
name: crossprovider codex concurrent-write-safety-in-reconciliation-requir
description: Concurrent write safety in reconciliation requires explicit locking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-safety, concurrent-writes, reconciliation]
---

Transactional reconcilers must refuse to mutate shared state when uncataloged live entries are detected. When parallel writers are possible, use pathspec-limited commits (`git commit -- <file>`) instead of broad sweeps to prevent race conditions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
