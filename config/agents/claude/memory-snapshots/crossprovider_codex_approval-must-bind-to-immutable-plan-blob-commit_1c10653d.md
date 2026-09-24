---
name: crossprovider codex approval-must-bind-to-immutable-plan-blob-commit
description: Approval must bind to immutable plan-blob commits, not transient labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gating, immutability, freshness-binding]
---

Approval gating must cite exact commit SHA; checkout-dependent freshness checks fail across rebases/drifts. Store approval as `approved-by: commit-sha` and fail-closed if commit becomes unreachable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
