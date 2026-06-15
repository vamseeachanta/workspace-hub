---
name: crossprovider codex downstream-data-contracts-require-all-fields-nee
description: Downstream data contracts require all fields needed by validators
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-contracts, integration, handoff]
---

When a summary payload feeds downstream validation, omitting required fields (captured_at, refresh_strategy, blocker_evidence) breaks the contract silently. Verify all downstream-required fields are in the summary before moving data along the pipeline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
