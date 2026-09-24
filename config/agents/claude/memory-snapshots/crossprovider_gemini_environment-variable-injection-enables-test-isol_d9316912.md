---
name: crossprovider gemini environment-variable-injection-enables-test-isol
description: Environment variable injection enables test isolation without file copying
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testability, design-pattern, test-fixtures]
---

QUEUE_ROOT / --queue-root pattern allows scripts to override directory paths at runtime. Tests set this to $TMPDIR, avoiding fixture file copying, symlink management, and live-queue pollution. Cleaner than path-based mocking.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
