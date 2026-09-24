---
name: crossprovider codex explicit-three-state-ownership-semantics-prevent
description: Explicit three-state ownership semantics prevent data integrity bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-modeling, error-handling, state-management]
---

When scripts manage ownership relationships (parent-child, feature-member), three cases must be explicit: (1) already owned by same parent → no-op idempotent, (2) owned by different parent → hard fail with clear error, (3) unowned → proceed. Implicit handling or silent skipping on conflict creates queue corruption and ownership ambiguity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
