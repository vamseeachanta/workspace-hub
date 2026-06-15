---
name: crossprovider codex merge-verification-report-row-counts-to-prove-un
description: Merge verification: report row counts to prove union correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [merge, verification, evidence]
---

After union-merging CSVs, report per-file row counts (ours / theirs / merged) to prove the merge was exhaustive and no rows were dropped. Verify all conflict markers are removed and `git diff --check` passes. This evidence protects against silent data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
