---
name: crossprovider codex telemetry-session-attribution-collapses-under-co
description: Telemetry session attribution collapses under concurrent load
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [telemetry, observability, instrumentation]
---

~42% of recent post-hook records lack session_id and tool name, rendering them unattributable. Loss correlates with parallel worktree activity. Schema-wide mandatory session ID at hook time is required; current unknown-tool filtering masks the depth of the gap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
