---
name: crossprovider hermes merge-safe-with-unrelated-ci-red-on-unprotected-
description: Merge safe with unrelated CI red on unprotected branches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [merge-decision, ci-health, branch-protection]
---

PR is mergeable if diff scope does not touch failing surface, failure is tracked separately in acknowledged issue, and branch has no required status checks. Document decision explicitly to avoid normalizing exceptions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
