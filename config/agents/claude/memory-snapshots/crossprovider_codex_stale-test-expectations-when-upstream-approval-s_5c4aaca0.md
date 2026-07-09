---
name: crossprovider codex stale-test-expectations-when-upstream-approval-s
description: Stale test expectations when upstream approval status changes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [test-drift, upstream-deps, status-sync]
---

Approval markers for upstream features (e.g., #66/#67) can advance while downstream schema validators still carry stale test expectations (status: plan-review). Caused flaky schema-validation failures in parallel sessions. Keep test expectations tied to actual approval markers in metadata, not hardcoded status strings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
