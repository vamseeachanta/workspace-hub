---
name: crossprovider codex input-validation-for-ledger-consistency-requires
description: Input validation for ledger consistency requires field-level equality on disposition-driving columns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, test-coverage, ledger-consistency]
---

When consuming a queue JSONL plus JSON report to produce a disposition ledger, validating only opaque_route_id matching is insufficient. Disposition values depend on routing_outcome and boundary_review_state, so validation must enforce full field-level equality for all disposition-driving columns. Otherwise manual fixture edits or data drift can slip through tests that only check ID uniqueness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
