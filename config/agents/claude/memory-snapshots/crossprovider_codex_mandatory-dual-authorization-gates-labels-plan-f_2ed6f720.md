---
name: crossprovider codex mandatory-dual-authorization-gates-labels-plan-f
description: Mandatory dual authorization gates: labels + plan files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [governance, authorization, git-workflow]
---

GitHub labels alone are insufficient. Implementation requires both the status label AND a `status:plan-approved/<issue>.md` file committed to main. Label without file allows review to be forgotten; file without label is undiscoverable. Both required.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
