---
name: crossprovider codex concurrent-pytest-runs-produce-cache-conflicts-i
description: Concurrent pytest runs produce cache conflicts in shared worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, concurrency, cache]
---

Multiple pytest invocations in the same worktree create `.pytest_cache` and `__pycache__` contention; file locks on bytecode directories cause hangs. Read-only reviews should use `pytest -q` with bytecode disabled (e.g., via scoped/minimal runs) rather than full suite execution, or verify no other pytest processes are active.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
