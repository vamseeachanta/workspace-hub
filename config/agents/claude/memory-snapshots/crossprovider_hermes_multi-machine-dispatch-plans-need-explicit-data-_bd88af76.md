---
name: crossprovider hermes multi-machine-dispatch-plans-need-explicit-data-
description: Multi-machine dispatch plans need explicit data/harness matrices
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [distributed-systems, planning, cross-machine]
---

workspace-hub #2720 planning required itemizing what data each machine can access and which AI providers/Hermes state are ready per-machine. Telegram is a dispatch notification plane, not sync source; canonical sync is GitHub issues/comments + git state + routing records. Cross-machine readiness gaps must be inventoried before dispatch experiments.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
