---
name: crossprovider codex marker-file-false-positive-liveness
description: Marker-file false-positive liveness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [liveness-detection, automation, monitoring]
---

Automation scripts running in dry-run or stale mode leave marker files indicating success despite actual failure. Memory bridge systems reported `MEMORY-FRESH` based on timestamps despite dry-run preventing execution. Use explicit heartbeats or transaction journals; marker presence alone is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
