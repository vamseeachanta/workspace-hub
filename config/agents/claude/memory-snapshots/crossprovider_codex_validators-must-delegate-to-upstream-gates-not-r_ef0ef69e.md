---
name: crossprovider codex validators-must-delegate-to-upstream-gates-not-r
description: Validators must delegate to upstream gates, not reimplement checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [validation-architecture, code-reuse, gate-delegation]
---

When a validator is designed to consume upstream gates (#67, #61, #63), reimplementing the logic locally creates shadow versions that diverge from the source of truth. The #52 validator reimplemented sampling, metric, and evidence checks instead of calling the upstream validators, allowing it to accept malformed evidence the upstream gates would reject. Always call the authoritative validator function rather than copying its logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
