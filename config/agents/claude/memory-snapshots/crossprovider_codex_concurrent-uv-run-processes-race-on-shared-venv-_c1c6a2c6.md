---
name: crossprovider codex concurrent-uv-run-processes-race-on-shared-venv-
description: Concurrent uv run processes race on shared .venv rebuild
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [build-concurrency, test-isolation, python-tooling]
---

When multiple processes invoke `uv run` against the same project `.venv`, they can collide during concurrent initial/rebuild phases. Sequence `uv run` invocations or share a single process context in validation suites to ensure idempotent results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
