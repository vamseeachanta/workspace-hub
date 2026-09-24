---
name: crossprovider codex circular-issue-dependencies-break-on-stage-separ
description: Circular issue dependencies break on stage separation, not layering
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-planning, dependency-management]
---

When issue A depends on B, B depends on C, and C requires completion of A, break the cycle by separating logical stages (e.g., internal discussion draft vs. operational engagement vs. final cross-artifact review) and assigning each to a distinct issue with clear boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
