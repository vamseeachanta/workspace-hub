---
name: crossprovider codex downstream-issues-should-import-upstream-validat
description: Downstream issues should import upstream validators, not redefine schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, coordination, code-reuse]
---

When issue #N depends on validation functions from issue #M, import existing validators rather than redefining schema. Prevents duplication, schema divergence, and reduces maintenance burden when contracts evolve.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
