---
name: crossprovider codex hard-gates-requiring-write-result-file-first-con
description: Hard gates requiring 'write result file first' conflict with execution-layer unavailability
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hard-gate, scout-pattern, gate-design, execution-constraint]
---

Scout lanes with hard gate 'First action: write STARTED timestamp' cannot execute when all local paths (shell, REPL, patch) fail at sandbox startup or when result paths fall outside writable roots. Gate design must handle execution constraints; hard gates requiring unreachable artifact writes are design conflicts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
