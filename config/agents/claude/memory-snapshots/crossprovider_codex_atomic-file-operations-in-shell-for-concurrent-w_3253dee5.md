---
name: crossprovider codex atomic-file-operations-in-shell-for-concurrent-w
description: Atomic file operations in shell for concurrent work-item creation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, shell-patterns, file-safety]
---

For generating auto-created work items in multi-process environments, use flock on a state file + mktemp for temporary file + mv for atomic rename. Prevents race conditions and duplicate ID generation when multiple agents run concurrently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
