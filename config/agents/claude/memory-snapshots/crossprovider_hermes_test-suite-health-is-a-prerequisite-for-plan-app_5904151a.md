---
name: crossprovider hermes test-suite-health-is-a-prerequisite-for-plan-app
description: Test suite health is a prerequisite for plan approval gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-review, test-validation, approval-gate]
---

Plans that cite 'the existing test suite already covers X' must first verify the suite is not broken or incomplete. Broken baseline leads to broken approval gates; use independent test runs or suite analysis before trusting coverage claims.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
