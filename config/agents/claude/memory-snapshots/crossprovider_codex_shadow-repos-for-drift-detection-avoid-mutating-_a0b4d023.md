---
name: crossprovider codex shadow-repos-for-drift-detection-avoid-mutating-
description: Shadow repos for drift detection avoid mutating tracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [testing, git, validation]
---

When validating generated artifacts, regenerate in a temp shadow repository rather than working-tree-local files. Keeps validation passes/fails isolated from tracked state, enabling clean commit granularity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
