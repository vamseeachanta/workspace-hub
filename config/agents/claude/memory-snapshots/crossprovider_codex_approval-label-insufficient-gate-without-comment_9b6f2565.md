---
name: crossprovider codex approval-label-insufficient-gate-without-comment
description: Approval label insufficient gate without comment verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, workflow, github-labels]
---

GitHub `status:plan-approved` label is necessary but not sufficient for execution. Always check issue comments and parent/blocker links; approved issues may have explicit comments stating 'blocked by parent #X' or 'awaits input restoration.' Label + comment must both permit execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
