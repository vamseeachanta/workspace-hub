---
name: crossprovider hermes validators-checking-internal-consistency-miss-st
description: Validators checking internal consistency miss stale external state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, tdd, artifact-staleness]
---

A validator that verifies JSONL/CSV/summary alignment can pass stale artifact sets if the underlying source corpus changes. Fix: add --repo-root flag, recompute current corpus digest, and fail if artifact summary digest/count diverges from live state. TDD this with failing tests first.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
