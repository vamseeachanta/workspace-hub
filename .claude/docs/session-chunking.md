# Session Chunking Guide

Practical guidance for managing context budget across WRK sessions.

## When to Chunk

| Route | Chunk trigger | Strategy |
|-------|--------------|----------|
| A (simple) | > 40% budget | Finish current stage, then stop |
| B (medium) | > 70% budget | Stop at next natural break point |
| C (complex) | By design | Plan multi-session before Stage 8 |

## Natural Break Points

Stop at these boundaries to minimize resume overhead:

- **Stage boundaries** — after any stage gate exit artifact is written (preferred)
- **After Stage 9** (claim) — clean state before execution begins
- **After each AC checkpoint** — discrete deliverable complete
- **After a full file is written and tested** — no dangling edits
- **Before a hard gate** (Stages 1, 5, 7, 17) — user review is a natural pause

Avoid stopping mid-file-edit or mid-test-run — resume cost is high.

## What to Write Before Stopping

`checkpoint.sh` auto-captures:
- Current stage number and status
- `next_action` (next step to resume from)
- `context_summary` (brief state description)

If stopping mid-stage, add a manual note:
```bash
bash scripts/work-queue/checkpoint.sh WRK-NNN
# Then manually edit assets/WRK-NNN/checkpoint.yaml:
#   context_summary: "Completed AC-1 impl; AC-2 tests next"
```

## How to Resume

**Primary path** — loads checkpoint automatically:
```bash
/work run WRK-NNN
```

**Diagnostic/inspection path** — review checkpoint before running:
```bash
/wrk-resume WRK-NNN
```

The `/work run` path reads `checkpoint.yaml` and restores stage/next-action context.
Use `/wrk-resume` only when you want to inspect or correct the checkpoint first.

## Context Warning Utility

Call manually when you sense budget pressure:
```bash
bash scripts/hooks/context-monitor.sh --usage-pct <N>
```

Behaviour:
- `>= 70%` — writes WARN to `logs/context-monitor.log`
- `>= 80%` — additionally calls `checkpoint.sh` and writes `context-warning.yaml`
- Idempotent: safe to call multiple times at the same threshold

The utility is **not auto-fired**; call it explicitly when the UI shows high usage.

See `scripts/hooks/context-monitor.sh` for implementation details.
