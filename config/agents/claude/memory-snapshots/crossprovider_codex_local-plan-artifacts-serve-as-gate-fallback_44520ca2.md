---
name: crossprovider codex local-plan-artifacts-serve-as-gate-fallback
description: Local plan artifacts serve as gate fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, offline-workflows]
---

When GitHub connector is unavailable, plan artifacts exist locally at `docs/plans/` and approval markers at `.planning/plan-approved/`. Use these to confirm the gate (`OPEN` + `status:plan-approved`) without live GitHub access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
