---
name: crossprovider hermes approval-gate-requires-plan-re-review-after-late
description: Approval gate requires plan re-review after latest push
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, review-workflow, git-state]
---

Approval gate isn't just "was it reviewed" but "was it reviewed against the latest committed artifact". For #2488, multiple plan patches and push lock races mean review artifacts on disk may not match HEAD on origin/main. Gating rule: latest plan commit SHA must match the SHA of the artifact the reviewer cited.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
