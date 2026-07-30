---
name: crossprovider codex fail-open-gates-hide-correctness-defects
description: Fail-open gates hide correctness defects
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [architecture, correctness, gates]
---

Gates that convert errors to warnings or accept invalid states (e.g., post-generation errors → warnings, non-404 network failures → warnings) mask real integrity failures. Critical gates must fail-closed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
