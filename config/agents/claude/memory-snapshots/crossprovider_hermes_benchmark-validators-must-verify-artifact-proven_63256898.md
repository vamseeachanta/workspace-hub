---
name: crossprovider hermes benchmark-validators-must-verify-artifact-proven
description: Benchmark validators must verify artifact provenance, not just schema
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, artifact-integrity]
---

Checking only `schema_version` and `question_count` leaves room for stale or forged scorecards. Validators must cross-check `fixture_version`, `benchmark_version`, `run_date`, and corpus hash to prevent silent artifact staleness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
