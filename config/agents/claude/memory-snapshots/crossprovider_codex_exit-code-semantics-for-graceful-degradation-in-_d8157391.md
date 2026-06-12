---
name: crossprovider codex exit-code-semantics-for-graceful-degradation-in-
description: Exit code semantics for graceful degradation in review chains
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, orchestration, exit-codes]
---

When network/DNS resolution fails, returning exit 0 instead of 3 means orchestration chains skip that review gracefully rather than hard-failing. Design choice for transient unavailability: don't block the entire workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
