---
name: crossprovider codex hardcoded-matrix-classifications-don-t-respond-t
description: Hardcoded matrix classifications don't respond to source snapshot updates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [readiness-matrix, architecture, state-management]
---

When readiness/completeness matrices have hardcoded lane classifications (e.g., `standards-disposition=needs-follow-up`), updating only the source issue snapshot won't propagate those changes. The matrix generation logic needs explicit conditional logic gated on both-issues-implemented status to clear the lane.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
