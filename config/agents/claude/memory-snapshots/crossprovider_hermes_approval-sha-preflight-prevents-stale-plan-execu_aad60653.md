---
name: crossprovider hermes approval-sha-preflight-prevents-stale-plan-execu
description: Approval SHA preflight prevents stale-plan execution drift
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, approval-gates, plan-safety]
---

Record the reviewed plan SHA/blob SHA in `.planning/plan-approved/<issue>.md` and require a pre-implementation mismatch check. This prevents post-approval plan edits from drifting implementation away from what was actually reviewed and approved.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
