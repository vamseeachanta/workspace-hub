---
name: crossprovider hermes large-skill-evaluations-need-incremental-cached-
description: Large skill evaluations need incremental/cached output
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [performance, large-datasets, caching]
---

Evaluating 932+ skill files can timeout (60s on glob search, 300s on audit scripts). Use `--summary-only` flags, incremental output files, or cached prior runs to avoid re-evaluating the full corpus on each run.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
