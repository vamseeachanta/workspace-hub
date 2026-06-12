---
name: crossprovider hermes scoped-validation-over-blanket-operations-under-
description: Scoped validation over blanket operations under load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [performance-optimization, workspace-hub-scale, testing-pattern]
---

In workspace-hub under heavy parallel git load, avoid broad scans (e.g. `git status -z -uall`, blanket secret scans); instead use targeted `git diff -- <files>`, `grep` on specific paths, and scoped linting on changed files only. Reduces timeout risk and isolates verification to only the changed surface.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
