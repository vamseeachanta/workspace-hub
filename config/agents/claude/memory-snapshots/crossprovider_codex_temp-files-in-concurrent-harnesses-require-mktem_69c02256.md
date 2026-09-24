---
name: crossprovider codex temp-files-in-concurrent-harnesses-require-mktem
description: Temp files in concurrent harnesses require mktemp + trap cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness, bash, concurrency, temp-files]
---

Fixed temp paths (`/tmp/audit-<id>.txt`) collide on concurrent runs and leave garbage on partial failures. Use `TMPDIR=$(mktemp -d)` at script start with `trap 'rm -rf "$TMPDIR"' EXIT` to guarantee cleanup on all exit paths, including signal-induced exits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
