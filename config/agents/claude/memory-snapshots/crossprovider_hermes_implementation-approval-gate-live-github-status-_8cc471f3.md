---
name: crossprovider hermes implementation-approval-gate-live-github-status-
description: Implementation approval gate: live GitHub status + local marker file
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval, github-status, implementation-gate, markers]
---

Implementation is eligible only when BOTH conditions hold: live GitHub issue has `status:plan-approved` label AND matching `.planning/plan-approved/<issue#>.md` marker file exists locally; either absence blocks implementation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
