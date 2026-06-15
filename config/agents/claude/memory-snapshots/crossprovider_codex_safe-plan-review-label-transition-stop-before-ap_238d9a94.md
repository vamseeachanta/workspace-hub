---
name: crossprovider codex safe-plan-review-label-transition-stop-before-ap
description: Safe plan-review label transition: stop before approval gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, github-labels, approval-gates, workflow]
---

Moving a plan from draft→plan-review requires: (1) commit/push plan + review artifacts + evidence, (2) post evidence comment on GitHub issue with commit SHA and review paths, (3) add status:plan-review label only. Stop there; do not add status:plan-approved without explicit user authorization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
