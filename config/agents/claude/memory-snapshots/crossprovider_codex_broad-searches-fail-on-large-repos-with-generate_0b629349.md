---
name: crossprovider codex broad-searches-fail-on-large-repos-with-generate
description: Broad searches fail on large repos with generated data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, large-repos, workflows]
---

On repos with large generated/data directories (>10K files), broad `rg` or `find` commands are slow and unreliable, often missing specific files because noise crowds the results. Narrow targeted searches (specific paths, globs) are faster and more reliable than broad repo-wide patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
