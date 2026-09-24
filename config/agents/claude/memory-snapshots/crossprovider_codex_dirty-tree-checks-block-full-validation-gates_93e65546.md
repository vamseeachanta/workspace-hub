---
name: crossprovider codex dirty-tree-checks-block-full-validation-gates
description: Dirty-tree checks block full validation gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, git, validation]
---

Some test suites reject any uncommitted changes in src/ (e.g., openfoam batch identity), forcing intermediate commits before running the full suite. Subset tests passing does not mean the full gate passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
