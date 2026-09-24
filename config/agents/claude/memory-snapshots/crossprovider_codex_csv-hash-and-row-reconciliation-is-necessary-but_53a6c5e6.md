---
name: crossprovider codex csv-hash-and-row-reconciliation-is-necessary-but
description: CSV hash and row reconciliation is necessary but insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, data-integrity, artifacts]
---

Files with matching hashes and row counts can still fail deeper validation: missing cross-checks, blank keys, absent units, incomplete lineage. Hash reconciliation verifies file identity, not semantic completeness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
