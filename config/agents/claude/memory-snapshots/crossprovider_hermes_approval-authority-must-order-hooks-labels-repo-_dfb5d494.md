---
name: crossprovider hermes approval-authority-must-order-hooks-labels-repo-
description: Approval authority must order: hooks > labels > repo > ledger > remote
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, source-of-truth, approval-ordering]
---

Split-brain failures occur when approval evidence exists across multiple sources with ambiguous precedence. Establish strict ordering: enforcement hooks (gates) are authoritative, GitHub labels are advisory-only, repo-tracked markers override labels, optional ledger state is consume-only and never authoritative, remote routine state is informational only. This prevents accidental dispatch on weak evidence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
