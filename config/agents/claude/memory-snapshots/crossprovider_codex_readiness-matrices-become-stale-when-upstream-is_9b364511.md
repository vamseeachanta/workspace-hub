---
name: crossprovider codex readiness-matrices-become-stale-when-upstream-is
description: Readiness matrices become stale when upstream issues change gate status without explicit row update
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [dependency-tracking, stale-state, readiness-matrix]
---

When an upstream issue (e.g., #723) moves from 'needs-decision' to 'plan-approved', dependent rows in the readiness matrix can show conflicting states if the builder definition is not refreshed. Matrix rows depend on live issue labels but also carry cached blocker/verification status fields — both must be reconciled on rebuild.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
