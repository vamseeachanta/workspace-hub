---
name: crossprovider codex redact-secrets-at-return-boundary-not-output-lay
description: Redact secrets at return boundary, not output layer
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [secrets, python-patterns, return-contracts]
---

Functions advertising 'secret-free' contracts must redact at the return boundary where the contract is defined, not only at CLI output. Downstream code invoking the function directly bypasses output-layer redaction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
