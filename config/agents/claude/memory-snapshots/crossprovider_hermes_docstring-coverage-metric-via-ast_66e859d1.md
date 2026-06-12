---
name: crossprovider hermes docstring-coverage-metric-via-ast
description: Docstring coverage metric via AST
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-quality, documentation]
---

Track public-function docstring ratio: (docstring-markers / public-defs). Ratio <0.7 indicates files needing attention. Use AST parsing to skip private/underscore functions. Files with ratio 0.04-0.5 are worst offenders. Google-style (Args/Returns/Raises) is standard across digitalmodel packages.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
