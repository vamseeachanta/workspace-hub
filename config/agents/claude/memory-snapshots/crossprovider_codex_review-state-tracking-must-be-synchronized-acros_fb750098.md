---
name: crossprovider codex review-state-tracking-must-be-synchronized-acros
description: Review state tracking must be synchronized across artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [review-tracking, coordination, consistency]
---

When a review verdict appears in multiple places (plan header, coordination ledger, results directory), it must be consistent. Session 6 found Gemini review marked PENDING in plan, not-run in ledger, and UNAVAILABLE in artifact—the inconsistency blocked approval quorum.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
