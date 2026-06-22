---
name: crossprovider codex multi-faceted-conditions-require-multi-faceted-p
description: Multi-faceted conditions require multi-faceted proof states
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [gate-logic, state-machines, blocker-removal]
---

Parent blocker gates that depend on duplicate-proof, provenance, retention, and owner-approval need separate state enums, not coarse single conditions. Duplicate proof alone should not unblock if provenance/retention/approval unresolved; gates must check all facets explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
