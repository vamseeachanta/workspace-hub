---
name: crossprovider codex approval-markers-fall-out-of-sync-with-neighbori
description: Approval markers fall out of sync with neighboring review states
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [approval-tracking, review-status, drift]
---

Missing `.planning/plan-approved/N.md` when adjacent artifacts are approved signals review drift. Check for asymmetries in artifact approval status; they indicate silent gaps in gate coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
