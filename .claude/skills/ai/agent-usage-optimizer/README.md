# agent-usage-optimizer

Reads `~/.cache/agent-quota.json` and recommends optimal Claude / Codex / Gemini
allocation for upcoming tasks or work-queue items.

## Trigger

```
/agent-alloc
/agent-alloc [task description]
/agent-alloc route-a | route-b | route-c
```

## Quick Start

1. Run `/agent-alloc` at the start of any work session.
2. Review the quota headroom table and recommended routing.
3. Accept the allocation or request an override before the plan gate.

## Cache Dependency

The skill reads `~/.cache/agent-quota.json` (populated by `query-quota.sh`).
If the cache is missing or older than 1 hour, it warns and falls back to
default routing rules — no external network calls are required.

## Route Summary

| Route | Complexity | Default Primary  |
|-------|-----------|-----------------|
| A     | Simple    | Codex            |
| B     | Standard  | Claude Sonnet    |
| C     | Compound  | Claude Opus      |
| Bulk  | —         | Claude Haiku     |
| Long  | —         | Gemini           |

When Claude quota drops below 20%, Routes B and C are automatically
rerouted to Codex and Gemini with a confirmation prompt.

## Full Documentation

See `SKILL.md` for complete routing logic, keyword classification,
quota thresholds, and work-queue integration format.
