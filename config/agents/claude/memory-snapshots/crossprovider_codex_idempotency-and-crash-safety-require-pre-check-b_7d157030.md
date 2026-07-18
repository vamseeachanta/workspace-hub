---
name: crossprovider codex idempotency-and-crash-safety-require-pre-check-b
description: Idempotency and crash-safety require pre-check before mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [mutations, idempotency, crash-safety]
---

Before creating GitHub issues or other state mutations, search for existing state to detect partial completion or crashes. Interruption after create but before attachment or commitment creates orphans. No preflight means reruns duplicate rather than resume.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
