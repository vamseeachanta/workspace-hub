---
name: crossprovider codex issue-label-transitions-require-evidence-trails-
description: Issue label transitions require evidence trails and README sync
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-pattern, approval-gates, evidence-trail]
---

Moving an issue through gates (draft → plan-review → plan-approved) requires: (1) plan file and README row committed/pushed, (2) evidence comment with reviewed commit SHA + plan path + provider verdicts, (3) label update only. Immediately verify README row status matches new label to prevent drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
