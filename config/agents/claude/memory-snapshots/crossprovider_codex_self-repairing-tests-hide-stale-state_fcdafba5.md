---
name: crossprovider codex self-repairing-tests-hide-stale-state
description: Self-repairing tests hide stale state
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [testing, test-design, generated-artifacts]
---

When test code rewrites generated artifacts before asserting on them, stale outputs get silently repaired instead of failing, masking divergence from the generator. Separate setup/generation from validation; tests must fail-fast on artifact staleness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
