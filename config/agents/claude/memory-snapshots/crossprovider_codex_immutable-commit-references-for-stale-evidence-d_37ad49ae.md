---
name: crossprovider codex immutable-commit-references-for-stale-evidence-d
description: Immutable commit references for stale-evidence detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-validation, workflow-gates, reproducibility]
---

File modification times and inferred timestamps are not machine-checkable or deterministic. Use git commit hashes as the canonical dating mechanism for workflow evidence—this enables deterministic staleness checks and audit trails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
