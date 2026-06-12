---
name: crossprovider codex policy-is-live-reference-respect-old-paths-befor
description: Policy is live reference: respect old paths before migrating
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migration, refactoring, policy-respect]
---

If repo policy docs still name `specs/` as canonical (even if outdated), and tests/config hardcode `specs/` paths, a one-shot migration is wrong. Phase 1 should be: inventory, classify (move/defer/archive), update only the references for items you move. Leave the rest until Phase 2.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
