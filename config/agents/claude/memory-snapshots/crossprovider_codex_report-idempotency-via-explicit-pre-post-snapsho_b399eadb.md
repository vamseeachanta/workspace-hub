---
name: crossprovider codex report-idempotency-via-explicit-pre-post-snapsho
description: Report idempotency via explicit pre/post snapshots, not runtime inference
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [idempotency, report-generation, state-tracking]
---

Deriving report fields (changed_paths, dataset_inventory) from runtime behavior creates invocation-sensitive reports—second run reports zero changes even if report itself is overwritten. Compare against baseline (git diff --name-only, or pre/post snapshot) instead. Separate what-was-computed-this-run from what-actually-changed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
