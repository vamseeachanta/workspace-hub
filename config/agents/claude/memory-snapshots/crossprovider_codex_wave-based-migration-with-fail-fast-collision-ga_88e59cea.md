---
name: crossprovider codex wave-based-migration-with-fail-fast-collision-ga
description: Wave-based migration with fail-fast collision gating
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-strategy, governance, safety]
---

Failing fast on pre-existing target files in the first wave (no overwrite policy) prevents silent data loss and enables separate waves to handle edge cases. Each wave is independently safe with explicit scope delineation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
