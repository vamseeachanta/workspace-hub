---
name: crossprovider codex idempotence-requires-two-full-runs-on-identical-
description: Idempotence requires two full runs on identical input, not just one-pass green
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [testing, idempotence, tdd, determinism]
---

Sync and merge code must be tested by running twice on the same input and verifying no divergence. A single passing run does not guarantee deterministic behavior; a second run can expose state-machine drift that one-pass test suites miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
