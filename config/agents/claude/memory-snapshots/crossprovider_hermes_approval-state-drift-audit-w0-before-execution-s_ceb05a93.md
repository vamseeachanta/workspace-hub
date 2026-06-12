---
name: crossprovider hermes approval-state-drift-audit-w0-before-execution-s
description: Approval-state drift audit (W0) before execution swarms
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workflow, approval-gates, kanban]
---

Before launching multi-issue work swarms, run a W0 live-state audit to detect issues that appear status:plan-approved on GitHub but show status:working locally, or vice versa. Prevents wasted swarm launches on stale/blocked work. Report identifies exact drift issues and blocker conversions needed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
