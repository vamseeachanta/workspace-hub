---
name: crossprovider hermes multi-machine-readiness-has-coordinator-vs-worke
description: Multi-machine readiness has coordinator vs. worker distinction
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, multi-machine, dispatcher-role, token-locality]
---

Dispatcher coordinator (ace-linux-1) and worker nodes (ace-linux-2) may have different readiness requirements. Workers dispatching over SSH to coordinator may not need local bot token; verify role before enforcing env var requirements.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
