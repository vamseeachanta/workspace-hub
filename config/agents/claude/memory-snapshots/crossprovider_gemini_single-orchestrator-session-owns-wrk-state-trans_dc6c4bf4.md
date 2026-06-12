---
name: crossprovider gemini single-orchestrator-session-owns-wrk-state-trans
description: Single orchestrator session owns WRK state transitions
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [session-binding, work-queue, governance, concurrency]
---

Only the active orchestrator session can transition a WRK between lifecycle states (Claim, Execute, Close, Archive); subagents execute work but cannot independently change state. Prevents race conditions and lost work. Enforced in WRK-624 canonical lifecycle.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
