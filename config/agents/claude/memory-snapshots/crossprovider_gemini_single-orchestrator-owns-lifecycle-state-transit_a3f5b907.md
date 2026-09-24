---
name: crossprovider gemini single-orchestrator-owns-lifecycle-state-transit
description: Single orchestrator owns lifecycle state transitions to prevent races
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [concurrency, state-management, multi-agent]
---

In multi-agent work processing, only a single orchestrator session should own stage transitions (pending → working → done → archived). Subagents execute but do not independently close or archive. Prevents race conditions and preserves traceability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
