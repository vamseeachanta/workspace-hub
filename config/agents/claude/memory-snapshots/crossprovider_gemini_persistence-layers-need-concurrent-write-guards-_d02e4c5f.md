---
name: crossprovider gemini persistence-layers-need-concurrent-write-guards-
description: Persistence layers need concurrent-write guards for shared files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, file-safety, persistence]
---

Use flock() to serialize writes to shared knowledge/memory files when multiple processes may access them. Prevents corruption from simultaneous writes in nightly cron + interactive session scenarios.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
