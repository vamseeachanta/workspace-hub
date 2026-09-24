---
name: crossprovider codex idempotent-installations-must-handle-no-final-ne
description: Idempotent installations must handle no-final-newline edge case
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [installation, idempotency, file-handling]
---

When appending to existing files, absence of a final newline causes the new content to be joined with the last line, breaking both parsing and idempotency. Always ensure a separating newline before appending markers or code blocks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
