---
name: crossprovider hermes staged-artifacts-must-validate-against-documente
description: Staged artifacts must validate against documented plan state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [decision-records, plan-approval-gates, staged-validation, hard-gates]
---

Issue #2766 implementation staged changes while the plan's decision-record still showed `plan-review` status. Implementation proceeded despite documented pre-approval gate. Decision records (plans/README) are part of the contract and must be validated during staged-diff review, not assumed stale.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
