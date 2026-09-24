---
name: crossprovider codex path-fallback-masks-config-validity-errors
description: Path fallback masks config validity errors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, config-validation, fail-closed-design]
---

A try/except that falls back to committed defaults when config load fails creates false safety; users don't know the source-of-truth config is broken. Better to fail closed and let the exception propagate. Only use explicit opt-in flag if fallback is intentional (e.g., compatibility mode).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
