---
name: crossprovider hermes semantic-contracts-require-explicit-test-enforce
description: Semantic contracts require explicit test enforcement in validators
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, contracts, testing, semantics]
---

Issue #2487's MAJOR blocker: validator enforced structural validity (valid YAML, required fields) but missed semantic contract (dispatch dependency_issues must mirror actionable issue_refs). Structural tests passed silently while semantic correctness failed. For future validators, explicit test cases binding contract clauses to assertion methods prevent silent drift.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
