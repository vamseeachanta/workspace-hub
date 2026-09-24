---
name: crossprovider gemini state-file-mirroring-enables-hook-to-agent-coord
description: State file mirroring enables hook-to-agent coordination
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hook-coordination, state-persistence, session-integration]
---

session_record_stage() mirrors WRK state to .claude/state/active-wrk file for hooks to read (hooks can't access session state). Hooks validate traceability against this file. Lightweight coordination pattern avoiding database/RPC infrastructure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
