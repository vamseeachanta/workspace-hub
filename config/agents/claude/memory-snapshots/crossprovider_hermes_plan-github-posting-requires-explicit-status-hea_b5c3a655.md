---
name: crossprovider hermes plan-github-posting-requires-explicit-status-hea
description: Plan GitHub posting requires explicit status header update, separate from review approval
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-posting, status-markers, git-flow]
---

#2665 plan passed all review rounds and underwent revision cycles, but the local plan header retained stale text ('pending re-review', 'not approved for implementation'), blocking GitHub posting. Posting requires explicit header edit to status: plan-review or equivalent—not just implicit readiness from review artifacts. Header update is a separate, manual gate from review approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
