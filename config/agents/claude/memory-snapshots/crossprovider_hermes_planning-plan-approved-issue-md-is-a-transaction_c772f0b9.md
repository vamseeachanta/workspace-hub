---
name: crossprovider hermes planning-plan-approved-issue-md-is-a-transaction
description: .planning/plan-approved/<issue>.md is a transactional gate, not a marker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [process, gates, repo-structure]
---

Implementation cannot proceed until .planning/plan-approved/<issue>.md exists locally with neutral operator/user approval wording AND is committed in the same transaction as the implementation changes. Gate is load-bearing; missing or staged-separately defeats the guard.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
