---
name: crossprovider codex probe-driven-review-catches-policy-bypasses-that
description: Probe-driven review catches policy bypasses that tests and diffs miss
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-methodology, adversarial-testing, policy-validation]
---

Static diff-reading and existing test passes cannot expose policy-level bypasses (e.g., shape-only evidence passing gate checks, string literals forging proof). Adversarial reviews must run concrete probes with hostile inputs (mixed tokens, malformed snapshots, enum-violating records, custom contracts) to verify fail-closed behavior empirically. This is load-bearing for security and policy validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
