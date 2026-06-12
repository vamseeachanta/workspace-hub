---
name: crossprovider hermes lane-keepers-must-not-github-mutate-mutations-st
description: Lane keepers must not GitHub-mutate; mutations stay in control plane
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [autonomy-bounds, github-safety, control-plane-pattern]
---

Autonomous lane keepers must not merge PRs, close issues, remove labels, hard-reset, or clean primary checkout. Keep GitHub mutations (issue comments, labels, closures, regressions) in human-controlled surface (ace-linux-1 control plane) for auditability and safety.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
