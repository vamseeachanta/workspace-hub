---
name: crossprovider codex phased-migration-strategy-for-large-directory-tr
description: Phased migration strategy for large directory trees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration, scoping, tdd, large-scale-refactoring]
---

When migrating or refactoring large trees, inventory first and classify content by lifecycle stage: move-now (actively used), defer (needs downstream migration), archive (reference/legacy). Write tests for Phase 1 moves before touching files, update only the references required for Phase 1 items, and document Phase 2 blockers. This prevents one-shot migrations that break still-live references.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
