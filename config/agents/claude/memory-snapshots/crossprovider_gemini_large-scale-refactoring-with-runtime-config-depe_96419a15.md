---
name: crossprovider gemini large-scale-refactoring-with-runtime-config-depe
description: Large-scale refactoring with runtime config dependencies requires phased approach
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [refactoring, runtime-config, phasing, WRK-204]
---

When renaming paths that are loaded by framework code (e.g., config loaders), breaking changes occur silently if framework references aren't updated alongside the rename. Phasing strategy: zero-risk renames first (docs/examples), then bulk operations, then critical framework updates (requires code review gate). Validate with checksums before and after.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
