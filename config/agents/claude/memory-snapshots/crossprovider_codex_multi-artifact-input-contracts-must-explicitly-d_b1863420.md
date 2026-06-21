---
name: crossprovider codex multi-artifact-input-contracts-must-explicitly-d
description: Multi-artifact input contracts must explicitly declare all inputs and fail-closed on schema coherence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [contracts, architecture, plan-design, multi-artifact-workflows]
---

When a script/plan consumes multiple interdependent artifacts (e.g., JSON report + JSONL ledger), declare both as explicit required inputs upfront. Validation must fail if schema/gate_status fields in one artifact mismatch or are missing in the other. Do not say 'consume only JSONL' if implementation requires schema/gate_status fields that only exist in the JSON report.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
