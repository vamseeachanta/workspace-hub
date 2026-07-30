---
name: crossprovider codex dependency-relationships-require-structured-vali
description: Dependency relationships require structured, validator-checkable representation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [dependencies, structured-data, validator-enforcement]
---

Prose mentions of upstream/downstream issue numbers in plan text are fragile. Store explicit dependencies in structured artifacts (e.g., JSON coordination registry with `depends_on` arrays) that validators can enforce and check for accidental mutations. Decouples dependency verification from plan review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
