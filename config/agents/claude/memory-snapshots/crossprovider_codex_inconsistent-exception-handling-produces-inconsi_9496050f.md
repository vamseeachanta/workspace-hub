---
name: crossprovider codex inconsistent-exception-handling-produces-inconsi
description: Inconsistent exception handling produces inconsistent CLI exits
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [cli-design, error-handling, testing]
---

When some code paths catch and transform exceptions (returning a result) while others propagate them (exiting non-zero), the same error produces inconsistent CLI behavior (exit 0 with embedded error vs. exit 1). Normalize exception handling at the CLI boundary or document the inconsistency explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
