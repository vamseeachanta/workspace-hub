---
name: crossprovider codex fail-open-vs-fail-closed-for-audit-control-code
description: Fail-open vs fail-closed for audit/control code
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, audit, gates, control]
---

Integration points favor fail-open (`|| true`) for resilience, but control gates and audit logging must be fail-closed. Silent fallback in audit code creates blind spots with no durable signal that logging failed; exception-based enforcement gates must abort to maintain the contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
