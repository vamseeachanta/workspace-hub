---
name: crossprovider gemini concurrent-file-appends-need-flock-with-timeout
description: Concurrent file appends need flock with timeout
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, file-operations, locking]
---

Use `flock` to guard concurrent writes to shared log files; include timeout to prevent indefinite hangs. Fail if lock cannot be acquired within timeout. WRK-658 implementation requirement.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
