---
name: crossprovider codex work-queue-integrity-checks-are-load-bearing-aut
description: Work queue integrity checks are load-bearing automation dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [work-queue, automation, integrity, gates]
---

Duplicate WRK IDs, stale state counters, and plan-gate violations corrupt queue semantics and automation (WRK-149 duplicates, state.yaml lagging behind active items). Systematic pre-ops audits (duplicate detection, state/index consistency, gate compliance per item) must run before any queue-based execution; integrate checks into `scripts/operations/compliance/` to detect violations early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
