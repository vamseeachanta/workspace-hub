---
name: crossprovider codex tier-status-or-classification-rules-must-be-full
description: Tier, status, or classification rules must be fully specified as state machines before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, classification, acceptance-criteria]
---

Ambiguous transitions (e.g., 'demote when invocations=0' without target tier or conditions) make implementation correctness impossible to verify. Define the complete state machine, edge cases, and test coverage before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
