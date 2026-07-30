---
name: crossprovider codex atomicity-tests-must-observe-construction-order-
description: Atomicity tests must observe construction order, not just method calls
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, atomicity, provider-routing]
---

Verifying preflight completion before provider construction requires observing construction timing, not downstream method calls. A regression constructing side-effects before preflight completes will pass method-call-only tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
