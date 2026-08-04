---
name: crossprovider codex record-based-state-with-schema-beats-label-based
description: Record-based state (with schema) beats label-based state for observability
metadata:
  type: reference
  source: codex
  bridged: 2026-08-01
  tags: [state-machine, reliability, record-schema]
---

Records (JSON with started_at/finished_at/returncode) are authoritative because they survive API failures, carry evidence, and enable compare-and-swap via git. Labels should be projections, not source-of-truth; confusing these roles hides failures and prevents reconciliation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
