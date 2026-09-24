---
name: crossprovider codex timeout-fallback-for-slow-or-unreliable-filesyst
description: Timeout fallback for slow or unreliable filesystems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem-reliability, timeout-handling, slow-storage]
---

When filesystem metadata operations timeout, report explicit "unknown" rather than inferring clean state. Preserves correctness on slow or unreliable storage; don't retry or infer completion based on unavailable probes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
