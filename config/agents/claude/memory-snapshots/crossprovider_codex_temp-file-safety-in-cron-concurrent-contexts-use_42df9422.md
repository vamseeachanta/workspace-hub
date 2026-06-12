---
name: crossprovider codex temp-file-safety-in-cron-concurrent-contexts-use
description: Temp file safety in cron/concurrent contexts — use mktemp with trap cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-patterns, cron-safety, concurrency]
---

Fixed-path temp files collide under concurrent or overlapping runs. Use `TMPDIR=$(mktemp -d)` at script start and `trap 'rm -rf "$TMPDIR"' EXIT` for automatic cleanup; per-artifact files within that directory avoid collision.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
