---
name: crossprovider hermes hard-gates-persist-even-in-agent-self-cycle-mode
description: Hard gates persist even in agent self-cycle mode
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, multi-agent, control-plane]
---

Even with bounded autofeed and multi-agent review lanes, control gates remain hard: no auto-application of `status:plan-approved`, no outreach/implementation without explicit user approval, no force-push/destructive cleanup. Control plane stays on primary machine (`ace-linux-1`); secondary machines (`ace-linux-2`) are overflow workers only, never GitHub mutators.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
