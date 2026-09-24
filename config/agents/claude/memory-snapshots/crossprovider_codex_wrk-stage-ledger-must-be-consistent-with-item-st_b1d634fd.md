---
name: crossprovider codex wrk-stage-ledger-must-be-consistent-with-item-st
description: WRK stage ledger must be consistent with item status before closure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, validation-gap, stage-evidence]
---

Items marked status:done and percent_complete:100 can still have stage ledger entries (Close, Archive) marked pending, creating an inconsistent close package. Enforce a validator that checks stage-evidence.yaml is fully completed (no pending stage rows) before allowing status:done transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
