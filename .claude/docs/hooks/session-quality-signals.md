# Session Quality Signals — Hook Architecture

> WRK-305 | Status: Signal 3 wired; Signals 1 & 2 pending native hook support.

## Overview

Three signals feed comprehensive-learning Phase 1 session-quality checks:

| Signal | Event | Status |
|--------|-------|--------|
| `context_reset` | `/clear` invocation | **Future wire-up** — see below |
| `plan_mode_start` / `plan_mode_end` | Plan-mode transitions | **Future wire-up** — see below |
| `session_tool_summary` | Per-WRK tool-call counts at Stop | **Wired** — `emit-session-quality-signals.sh` |

Signal file: `.claude/state/session-signals/YYYY-MM-DD.jsonl`

---

## Signal 3 — session_tool_summary (WIRED)

Hook: `.claude/hooks/emit-session-quality-signals.sh` (Stop hook)

```jsonl
{"ts":"ISO8601","event":"session_tool_summary","session_id":"<id>","wrk":"<active-wrk>","tool_calls":142,"edits":23,"reads":67}
```

Aggregates from `.claude/state/sessions/session_YYYYMMDD.jsonl` (written by
`session-logger.sh`) at Stop time. Active WRK detected from
`.claude/work-queue/working/`. Completes in < 1 second.

Registered in `.claude/settings.json` Stop hook block.

---

## Signal 1 — context_reset (FUTURE WIRE-UP)

### Why it cannot be wired today

`/clear` is a Claude Code built-in CLI command. As documented in
`.claude/docs/session-lifecycle.md` (Pre-Clear Workflow section):

> `/clear` **cannot be intercepted** by any hook (PreToolUse, PostToolUse,
> PreCompact, Stop).

Claude Code exposes no `PostClear`, `Notification`, or `UserPromptSubmit`
hook that fires before or after `/clear`. The command bypasses the hook
pipeline entirely.

### Workaround: /clear skill wrapper

Until Claude Code exposes a native hook, the recommended approach is a
`/clear` skill wrapper that emits the signal before delegating to the
built-in:

```markdown
# .claude/skills/workspace-hub/clear/SKILL.md
invoke: clear
```

When invoked via `/clear` (skill), the skill can:
1. Call `bash .claude/hooks/emit-context-reset.sh` to write the signal
2. Then let the user know to issue the built-in `/clear` command

Limitation: this only captures `/clear` invocations via the skill system.
Direct `/clear` CLI usage remains uninterceptable.

### Placeholder hook script

`.claude/hooks/emit-context-reset.sh` exists as a callable script.
Wire it from a `/clear` skill wrapper once the skill is created.

```bash
# Manual invocation (from /clear skill or ad-hoc):
bash .claude/hooks/emit-context-reset.sh [session_id] [active-wrk]
```

### Native hook — when available

Watch for `PostClear` or `UserPromptSubmit` hook event types in Claude Code
release notes. When available, register in `settings.json`:

```json
"PostClear": [
  {
    "matcher": ".*",
    "hooks": [{
      "type": "command",
      "command": "bash \"${WORKSPACE_HUB}/.claude/hooks/emit-context-reset.sh\""
    }]
  }
]
```

---

## Signal 2 — plan_mode_start / plan_mode_end (FUTURE WIRE-UP)

### Why it cannot be wired today

Claude Code plan-mode is a UI/session-level state toggle. There is no
`PrePlanMode`, `PostPlanMode`, or equivalent hook event in the current
hook system (`PreToolUse`, `PostToolUse`, `PreCompact`, `Stop`).

The `EnterPlanMode` / `ExitPlanMode` tool names referenced in the WRK spec
are not hook-interceptable tool calls — they are internal session state
transitions that do not pass through the `PostToolUse` pipeline.

### Placeholder hook script

`.claude/hooks/emit-plan-mode-signal.sh` exists as a callable script.

```bash
# Usage (from a future hook or manual invocation):
bash .claude/hooks/emit-plan-mode-signal.sh start [session_id] [active-wrk]
bash .claude/hooks/emit-plan-mode-signal.sh end   [session_id] [active-wrk] [approved]
```

### Native hook — when available

Watch for `PlanModeStart` / `PlanModeEnd` or `UserPromptSubmit` events in
Claude Code release notes. When available, register in `settings.json`
using a `matcher` that catches the relevant plan-mode transition events.

### Partial coverage: UserPromptSubmit (if added)

If Claude Code adds `UserPromptSubmit`, it fires when the user submits a
message — which includes approval messages in plan-mode. A heuristic
classifier in the hook script could infer plan-mode transitions from
message content. This is fragile but better than nothing.

---

## Phase 1 Behavior Without Wired Signals

The comprehensive-learning Phase 1 signal checks degrade gracefully:

| Check | Behaviour if signal absent |
|-------|---------------------------|
| Context reset discipline | `"signal not available — emitter not configured"` |
| Plan mode skipped | `"signal not available — emitter not configured"` |
| Task decomposition quality | Uses `session_tool_summary` — **available** |

Once Signals 1 and 2 are wired, re-run Phase 1 to populate historical gaps.

---

## Related

- `.claude/hooks/emit-session-quality-signals.sh` — Signal 3 (wired)
- `.claude/hooks/emit-context-reset.sh` — Signal 1 placeholder
- `.claude/hooks/emit-plan-mode-signal.sh` — Signal 2 placeholder
- `.claude/docs/session-lifecycle.md` — Pre-Clear Workflow section
- `comprehensive-learning` SKILL.md Phase 1 — consumes these signals
- WRK-305 — implementation tracking
