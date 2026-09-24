---
name: crossprovider codex atomic-file-writes-prevent-partial-state-in-cron
description: Atomic file writes prevent partial state in cron
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, file-operations, atomicity]
---

Always write to a temporary file, then atomic rename (atomic on most filesystems) to prevent partial state corruption on process interruption. Applies to any stateful cron/daemon that updates shared files. Protects against signal interruption or OOM kill mid-write.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
