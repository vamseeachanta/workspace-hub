---
name: crossprovider hermes hermes-multi-session-coordination-loss-under-con
description: Hermes multi-session coordination loss under context compression
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-quirk, context-compression, multi-session-coordination]
---

When Hermes spawns multiple agents on the same issue (e.g., 12+ sessions on #2665 in one day), each spinup loses context from prior attempts and restarts intake/draft cycles. Context-compression-induced task thrashing is a recurring failure mode.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
