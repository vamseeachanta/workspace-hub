---
name: crossprovider hermes batch-docstring-insertion-via-script-handle-sheb
description: Batch docstring insertion via script — handle shebang/encoding/blanks correctly
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [docstrings, bulk-edit, coverage]
---

Adding module-level docstrings to 50+ files atomically: read file, insert docstring after shebang/encoding declaration but before imports/code, add blank line after docstring. Script approach beats manual edits. Reusable pattern for coverage uplift; watch for pre-existing import errors (missing pint/plotly/deepdiff) masking real regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
