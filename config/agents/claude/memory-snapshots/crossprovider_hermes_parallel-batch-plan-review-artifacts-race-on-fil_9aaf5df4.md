---
name: crossprovider hermes parallel-batch-plan-review-artifacts-race-on-fil
description: Parallel batch plan review artifacts race on file writes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review-concurrency, batch-processing, file-safety]
---

Running `plan-review-fanout.sh` on 4 plans in parallel with `--output-dir=scripts/review/results` causes concurrent writes to overwrite/corrupt review artifacts. File contents go from populated to empty mid-batch. Mitigation: serialize review runs or use per-provider subdirectories with atomic renames.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
