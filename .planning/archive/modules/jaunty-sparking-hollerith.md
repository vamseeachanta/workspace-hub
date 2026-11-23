---
id: workspace-hub#1398
title: "Review scheduled tasks & fix daily summaries not surfacing"
status: done
route: B
audit_date: "2026-03-25"
spinoffs: [workspace-hub#1409, workspace-hub#1410, workspace-hub#1411]
---

# WRK-1398: Scheduled Tasks Audit & Daily Summary Fix

## Audit Summary (2026-03-25)

### Root Cause: Hostname Identity Mismatch

This machine is `ace-linux-1` but the entire scheduling infrastructure expects `dev-primary`.
Hostname-to-role mapping is **scattered across 6+ files** with no single source of truth.

| What | Expected | Actual |
|------|----------|--------|
| `hostname -s` | `dev-primary` | `ace-linux-1` |
| SSH alias `dev-secondary` | resolvable | not in /etc/hosts or ~/.ssh/config |
| Tailscale (10.1.0.1/2) | running | not installed |

### Machine Connectivity (2026-03-25)

| Machine | Physical Hostname | Reachable | Method |
|---------|------------------|-----------|--------|
| dev-primary | ace-linux-1 | Yes (local) | — |
| dev-secondary | ace-linux-2 | Yes (by physical name) | SSH to 192.168.1.103 |
| dev-secondary | — | No (by logical name) | `ssh dev-secondary` fails DNS |
| licensed-win-1 | — | No | unreachable |

### Cron Task Status (Last 30 Days)

| Task | Schedule | Status | Detail |
|------|----------|--------|--------|
| comprehensive-learning | Daily 2AM | Running (degraded) | Completes wrapper steps but **skips main pipeline** (hostname ≠ dev-primary). Only commits state and pushes. |
| agent-radar | Daily 2:30AM | **Broken** | `uv` not in cron PATH. 12 consecutive failures since install. |
| session-analysis | Daily 3AM | Running (bugs) | printf/arithmetic errors (lines 220, 274, 310, 319). Still produces output. |
| model-ids | Weekly Sun 3:30AM | Working | No issues. |
| skills-curation | Weekly Mon 4AM | **Broken** | Invalid CLI syntax: `claude --skill` not a valid flag. |
| claude-memory-backup | Daily 5AM | Unknown | 0-byte log since Mar 10. No diagnostic output. |
| repository-sync | Every 4h | Unknown | 0-byte log since Feb 24. Likely running silently. |
| ai-tools-status | Hourly | Working | Reports 2/3 machines unreachable. |

**Not in crontab (declared in YAML but never installed):**
- `/today` daily summary — last ran March 2 (manual only)
- dep-health, doc-drift, benchmark-regression, notification-purge

### Output Artifact Gaps

| Artifact | Location | Last Generated | Gap |
|----------|----------|---------------|-----|
| Learning reports | `.claude/state/learning-reports/` | Mar 19 | 6 days |
| Reflect history | `state/reflect-history/` | Mar 18 | 7 days |
| Daily logs (`/today`) | `logs/daily/` | Mar 2 | **23 days** |
| Session analysis | `.claude/state/session-analysis/` | Mar 24 | Current |
| Notification JSONL | `logs/notifications/` | Mar 25 | Current (but nothing reads them) |

### Architectural Issues Found

1. **Hostname mapping scattered**: `setup-cron.sh`, `comprehensive-learning.sh`, `validate-schedule.py`, `assign-workstations.py` (×2 copies), `machine-ranges.yaml`, `ssh-helpers.sh` — all hardcode machine names independently.
2. **notify.sh is a dead-letter queue**: Writes JSONL to `logs/notifications/` but nothing reads it. Purged after 7 days.
3. **Duplicate `assign-workstations.py`**: Identical copies in `scripts/work-queue/` and `.claude/skills/.../stage-03-triage/scripts/`.
4. **comprehensive-learning sub-steps invisible**: YAML shows 1 task; 12+ sub-steps run inside.
5. **No SSH config**: `~/.ssh/config` doesn't exist. Logical names `dev-primary`/`dev-secondary` unresolvable.

---

## Fix Plan (Not Yet Executed)

### Pragmatic Fix (this WRK)

| Step | File | Change |
|------|------|--------|
| 1 | `scripts/cron/setup-cron.sh` | Add `ace-linux-1` to case → `full` variant |
| 2 | `config/scheduled-tasks/schedule-tasks.yaml` | Add `ace-linux-1` to all dev-primary tasks; add `daily-today` task |
| 3 | `scripts/learning/comprehensive-learning.sh` | Accept `ace-linux-1` as primary hostname (line 29) |
| 4 | `scripts/analysis/session-analysis.sh` | Fix printf/arithmetic bugs (~lines 220, 274, 310, 319) |
| 5 | `scripts/cron/setup-cron.sh` | Run to re-install crontab from YAML |
| 6 | `~/.ssh/config` | Add `Host dev-secondary` → `ace-linux-2` alias |
| 7 | `docs/ops/scheduled-tasks.md` | New — living schedule inventory |

### Additional Broken Tasks to Fix

| Task | Fix |
|------|-----|
| agent-radar | Add `PATH=$HOME/.local/bin:$PATH` to crontab command |
| skills-curation | Rewrite CLI invocation (invalid `--skill` flag) |
| claude-memory-backup | Add timestamp echo for diagnostics |
| repository-sync | Add timestamp echo for diagnostics |

### Future Work (separate WRK)

- **Machine registry**: Create `config/machines/registry.yaml` as single source of truth for hostname→role mapping. Refactor all 6+ consumers to read from it.
- **Notification consumer**: Wire `/today` or a desktop notifier to read `logs/notifications/`.
- **Deduplicate `assign-workstations.py`**: Symlink or import from canonical location.

## Verification Results (2026-03-25)

| Check | Result |
|-------|--------|
| `uv run --no-project python scripts/cron/validate-schedule.py` | OK: 16 tasks validated |
| `bash scripts/cron/setup-cron.sh --dry-run` | 14 tasks for ace-linux-1 |
| `FORCE_RERUN=true bash scripts/analysis/session-analysis.sh 2>&1 \| grep -i error` | Clean — 0 errors |
| `crontab -l \| wc -l` | 14 entries installed |
| `bash scripts/productivity/daily_today.sh` | Generated 11.8KB `logs/daily/2026-03-25.md` |

## Completion Notes (2026-03-25)

- Crontab installed with 14 YAML-driven entries (replaced old 8-entry crontab)
- `session-analysis` added to YAML (was missing — would have been silently dropped)
- `claude-memory-backup` fixed to use `ace-linux-2` (physical hostname) instead of `dev-secondary`
- SSH config NOT needed — machines have direct access; cross-machine tasks execute independently
- `setup-cron.sh` has append-only bug — worked around by replacing crontab directly from dry-run output

## Spinoff WRK Items Created

| WRK | Title | Route |
|-----|-------|-------|
| 1409 | Create centralized machine registry (`config/machines/registry.yaml`) | B |
| 1410 | Fix skills-curation cron — invalid CLI invocation | A |
| 1411 | Wire notification consumer — surface notifications to `/today` | A |
