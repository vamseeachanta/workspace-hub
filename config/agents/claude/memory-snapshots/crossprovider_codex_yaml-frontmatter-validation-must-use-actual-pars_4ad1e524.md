---
name: crossprovider codex yaml-frontmatter-validation-must-use-actual-pars
description: YAML/frontmatter validation must use actual parser plus test fixtures with malformed input
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml, validation, testing]
---

Shell/grep checks miss syntax errors (e.g., unquoted colons). Delegate to PyYAML or equivalent; add test fixtures with invalid frontmatter and negative assertions to catch breakage deterministically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
