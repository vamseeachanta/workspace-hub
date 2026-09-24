---
name: crossprovider codex machine-independent-idempotency-specs-diverge-fr
description: Machine-independent idempotency specs diverge from actual implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [idempotency, multi-machine, specification-gap]
---

Plan pseudocode used `idempotency="issue:provider"` but live dispatch implements `issue:provider:machine`. Tests can pass while production has multi-machine double-dispatch. Mock tests cannot substitute for multi-machine integration tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
