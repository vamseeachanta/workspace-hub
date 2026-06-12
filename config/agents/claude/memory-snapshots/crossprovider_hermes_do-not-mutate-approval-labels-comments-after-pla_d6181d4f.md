---
name: crossprovider hermes do-not-mutate-approval-labels-comments-after-pla
description: Do not mutate approval labels/comments after plan patches without explicit waiver or fresh review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, process-discipline, github-workflow]
---

Plan-review and approval labels are gates, not metadata. After patching plan text to address reviewer findings, do not toggle labels without fresh evidence (explicit user waiver or clean cross-provider re-review result). Prevents false approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
