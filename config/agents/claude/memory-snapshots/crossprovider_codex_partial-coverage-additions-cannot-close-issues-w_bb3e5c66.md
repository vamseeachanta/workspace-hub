---
name: crossprovider codex partial-coverage-additions-cannot-close-issues-w
description: Partial coverage additions cannot close issues without full-field audit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [completeness-proof, issue-closure, test-coverage]
---

Adding 2 of 12 fields to a strict registry and leaving the rest marked `source_gap_fields` does not constitute issue closure. Tests must verify the complete current field set and prove that strict/default behavior is correct end-to-end before a `plan-approved` status can be claimed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
