---
name: crossprovider codex file-existence-is-prerequisite-for-reference-ver
description: File existence is prerequisite for reference verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, test-logic]
---

Cannot prove zero references in a file via `grep pattern file 2>/dev/null` if the file may be missing—the grep returns 0 either way. Plans claiming zero references must first explicitly verify file existence, or mark the verification unavailable if the file doesn't exist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
