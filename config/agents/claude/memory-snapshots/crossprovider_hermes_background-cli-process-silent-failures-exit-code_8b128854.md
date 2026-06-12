---
name: crossprovider hermes background-cli-process-silent-failures-exit-code
description: Background CLI process silent failures: exit code -15 produces 0-byte logs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [process-safety, error-handling, background-tasks]
---

Delegated processes (e.g. `claude -p <prompt> --max-turns 20 > log 2>&1`) can be killed mid-execution, leaving empty logs. No stderr indication of termination. Verify process liveness via `pgrep` before trusting log output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
