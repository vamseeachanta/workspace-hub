---
name: crossprovider codex scheduler-exception-boundaries-must-include-defe
description: Scheduler exception boundaries must include deferred operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, scheduler-architecture]
---

Issue #809: Fixture refresh ran after try-catch, exceptions escaped and lost job identity in retry logging. Deferred/async work OUTSIDE error handling breaks job context and failure reporting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
