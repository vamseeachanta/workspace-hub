---
name: crossprovider codex upstream-validator-baseline-integrity-is-load-be
description: Upstream validator baseline integrity is load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, validation, test-integrity]
---

Downstream issues (#52, #63) assume upstream dependencies (#66 token fixtures) are green, but #66's own unit test was failing on tracked forbidden-request-key violations. Plans cannot assume upstream validators pass without verification. Pre-plan audits must run upstream validators to ground baseline assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
