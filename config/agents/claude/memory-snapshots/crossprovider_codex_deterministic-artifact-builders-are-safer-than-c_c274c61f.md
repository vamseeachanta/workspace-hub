---
name: crossprovider codex deterministic-artifact-builders-are-safer-than-c
description: Deterministic artifact builders are safer than corpus-walking scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, safety, testability]
---

For routing/gating logic, prefer builders that consume already-validated tracked inputs (like readiness matrix rows) over new scripts that walk corpus directories. Builders have smaller blast radius, are easier to test, and can be audited without corpus access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
