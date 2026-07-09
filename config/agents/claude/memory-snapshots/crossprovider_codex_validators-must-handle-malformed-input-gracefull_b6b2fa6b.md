---
name: crossprovider codex validators-must-handle-malformed-input-gracefull
description: Validators must handle malformed input gracefully, not crash
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [error-handling, validator-contract, defect-pattern]
---

When validators receive non-object JSON, missing required fields, or invalid types at boundaries, they crash with unhandled tracebacks (AttributeError, KeyError) instead of returning structured DENY-style errors. This breaks downstream gates that expect consistent error envelopes. Wrap input validation in try-catch blocks that convert exceptions to explicit DENY responses with reason codes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
