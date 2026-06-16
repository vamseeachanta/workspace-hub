---
name: reference_claude_hooks_cannot_see_spend
description: "Claude Code PreToolUse hooks cannot see token/cost spend; cost is statusline-only — budget enforcement can't live in a hook"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 385fd1bf-9a54-47c7-b22d-573740acede8
---

A Claude Code **PreToolUse hook** stdin payload carries only `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id` — **no `cost`, `usage`, `rate_limits`, or cumulative tokens** (verified: `.claude/hooks/session-logger.sh:26-29` parses only tool_name/tool_input/session_id). `cost.total_cost_usd` is **statusline-payload-only** (`.claude/statusline-command.sh:18`), NOT available to hooks.

Consequences (G4 #3119, 2026-06-15):
- A hook **cannot hard-block on cumulative spend** — the data isn't there. The only hook-enforceable budget is a **tool-CALL count** (`session-governor-check.sh` / `tool-call-ceiling.sh` emit `{"decision":"block"}` keyed by `$PPID`).
- PreToolUse also fires too late + skips tool-less reasoning turns → can't "pause a runaway token burn."
- Workaround for context %: the statusline writes a bridge file (`gsd-statusline.js`→`/tmp/claude-ctx-<session>.json`) that PostToolUse hooks read back. Same pattern could plumb cost as a SOFT/advisory signal, but never a reliable hard block.
- True spend enforcement belongs at the **SDK/dispatch layer** (`ResultMessage.total_cost_usd` per `query()`), not a hook.
- `credit-utilization-tracker.py` is **weekly aggregate**, not per-session live.

General lesson (4th time this session): adversarial review keeps catching the same trap — a plan assuming a harness capability that doesn't exist (G1 capability-enforcement Claude-only; G3 MCP-client support; G4 hook-spend-visibility). Verify the capability empirically in Phase 0 BEFORE designing enforcement on top of it. Pairs with [[project_skill_retirement_blocked_on_invocation_signal]] (instrument real usage before acting).
