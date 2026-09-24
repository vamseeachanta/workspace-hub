---
name: crossprovider codex atomic-file-updates-via-tmp-rename-ensure-consis
description: Atomic file updates via .tmp + rename ensure consistency under concurrent access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, file-safety, atomicity, idempotency]
---

When multiple processes may write to the same file, use atomic write pattern: write to a temporary file with a known suffix (e.g., '.tmp'), then rename() to the target. Document that zero-change runs must still write to the log to preserve idempotency semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
