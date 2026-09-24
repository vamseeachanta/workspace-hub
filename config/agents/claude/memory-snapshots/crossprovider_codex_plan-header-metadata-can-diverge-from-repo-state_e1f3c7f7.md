---
name: crossprovider codex plan-header-metadata-can-diverge-from-repo-state
description: Plan header metadata can diverge from repo state; reconcile explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-metadata, state-drift, approval-markers]
---

If a plan's `Status:` field says `plan-review` but coordination and approval markers say `plan-approved`, document the reconciliation or update the header. Implicit metadata divergence creates confusion and gate-timing ambiguity downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
