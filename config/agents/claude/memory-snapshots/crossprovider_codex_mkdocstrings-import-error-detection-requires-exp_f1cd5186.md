---
name: crossprovider codex mkdocstrings-import-error-detection-requires-exp
description: mkdocstrings import-error detection requires explicit config
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [mkdocs, documentation, tooling, api-docs]
---

mkdocs build with mkdocstrings does not reliably fail on broken imports or API rot by default; handlers and strict mode must be configured explicitly. AC criteria like 'build fails on broken docstring imports' cannot be met by tool presence alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
