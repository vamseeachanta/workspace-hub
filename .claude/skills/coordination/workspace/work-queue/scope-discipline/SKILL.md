---
name: work-queue-scope-discipline
description: 'Sub-skill of work-queue: Scope Discipline.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Scope Discipline

## Scope Discipline


> **One feature per session.** Anthropic identifies "doing too much at once" as the core
> failure mode for long-running agents. The scope guard enforces this.

`set-active-wrk.sh` blocks activation of a new WRK when another is already active
and not `done` or `archived`. The guard writes a `started_at` timestamp on line 2
of `.claude/state/active-wrk`.

| Scenario | Behavior |
|----------|----------|
| No active WRK | Allows activation |
| Same WRK re-activated | Allows (idempotent) |
| Different WRK, current is `done`/`archived` | Allows overwrite |
| Different WRK, current is active | **Blocks** — exit 1 + `SCOPE_GUARD_WARNING` |
| `--force` flag | Bypasses guard (for archival scripts, multi-WRK ops) |

```bash
# Normal activation
bash scripts/work-queue/set-active-wrk.sh WRK-1234

# Force bypass (e.g., during archive-item.sh)
bash scripts/work-queue/set-active-wrk.sh WRK-5678 --force
```
