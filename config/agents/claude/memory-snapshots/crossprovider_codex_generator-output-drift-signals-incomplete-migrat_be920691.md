---
name: crossprovider codex generator-output-drift-signals-incomplete-migrat
description: Generator/output drift signals incomplete migration patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [migration-patterns, refactoring, documentation]
---

Large divergence between generated HTML and committed output usually means partial migration: templates updated without regenerating, or generators not updated to match new design language. Address by tracing the exact divergence path (hardcoded tokens, constructed paths, logo references) and regenerating deterministically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
