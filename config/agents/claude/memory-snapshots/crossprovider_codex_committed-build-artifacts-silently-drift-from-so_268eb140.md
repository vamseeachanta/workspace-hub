---
name: crossprovider codex committed-build-artifacts-silently-drift-from-so
description: Committed build artifacts silently drift from source code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [build-artifacts, ci-cd, testing]
---

When outputs (JSON bundles, CSVs, Parquet exports) are committed to the repo but source code evolves, a hidden mismatch develops: the artifact appears current but reflects stale logic. Catch this by regenerating committed outputs in CI and validating source-hash matching; otherwise false confidence leads to publication failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
