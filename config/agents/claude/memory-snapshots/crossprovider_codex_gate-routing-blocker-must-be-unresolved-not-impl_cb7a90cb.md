---
name: crossprovider codex gate-routing-blocker-must-be-unresolved-not-impl
description: Gate routing: blocker must be unresolved, not implemented evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [workflow, gates, blocker-semantics]
---

In workflow/readiness systems, distinguish `linked_issue_refs` (evidence/context trail) from `next_issue_ref` (active blocker). Gate logic must route to unresolved blockers, never to implemented issues. Readiness semantics collapse when a gate points to an already-completed step; that creates false 'ready' states.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
