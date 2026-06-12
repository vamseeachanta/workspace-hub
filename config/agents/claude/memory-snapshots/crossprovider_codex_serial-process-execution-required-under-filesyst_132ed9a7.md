---
name: crossprovider codex serial-process-execution-required-under-filesyst
description: Serial process execution required under filesystem stress
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [filesystem-stress, stalled-processes, serial-fallback]
---

Parallel npm/git/pytest processes stall when filesystem I/O saturates (parallel worktree materializations, multi-agent git). Rerun serially: `npm test -- --runInBand`, `pytest -n0`, bounded git commands. Allow 30-60s per operation; monitor output for progress.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
