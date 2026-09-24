---
name: crossprovider codex tdd-collection-parity-as-refactoring-validation-
description: TDD collection parity as refactoring validation gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, refactoring, test-integrity]
---

When refactoring tests structurally (splitting modules, consolidating fixtures), establish baseline collection metrics before changes, restructure, then verify exact parity of normalized node IDs and assertion counts afterward. This catches defects where test count stays identical but semantics drift (e.g., helper behavior changing from explicit-empty to default-substitution).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
