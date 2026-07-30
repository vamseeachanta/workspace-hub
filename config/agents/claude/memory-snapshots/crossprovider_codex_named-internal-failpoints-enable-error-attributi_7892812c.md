---
name: crossprovider codex named-internal-failpoints-enable-error-attributi
description: Named internal failpoints enable error attribution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [error-handling, resilience, recovery, diagnostics]
---

When operations can fail at multiple stages (mkdir, open, write, chmod), name each stage and record which stage failed in error residue. Error strings alone ('operation failed') don't tell recovery code how to handle it; stage names enable targeted recovery and retry logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
