---
name: crossprovider codex new-flags-in-multi-flag-scripts-need-explicit-in
description: New flags in multi-flag scripts need explicit interaction matrix tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, testing, scripts]
---

Adding `--docs` to a script with `--ruff-only` and `--mypy-only` requires documenting and testing all combinations. Inherited behavior is non-obvious; gaps cause silent drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
