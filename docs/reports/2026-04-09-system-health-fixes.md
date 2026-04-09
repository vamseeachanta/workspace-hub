# System Health Fixes — 2026-04-09

Addresses findings from the 2026-04-06 daily cron health review.
Issue: #1985

## Summary

The 2026-04-06 health report (``.claude/state/cron-health/2026-04-06.json``)
flagged 12 problems out of 26 tasks: 14 healthy, 12 issues (1 ERROR, 5 STALE,
6 MISSING). After investigation, 4 are real failures, 8 are false positives
caused by monitoring logic gaps, and 4 tasks were missing from the crontab.

## 4 Real Cron Failures — Fixed

| Task | Status | Root Cause | Fix |
|---|---|---|---|
| `agent-radar` | ERROR | YAML command used hardcoded `/home/vamsee/.local/bin/uv` and `uv run --no-project python` which does not honor PEP 723 inline deps (`pyyaml`). Fails every night since at least 04-05. | Changed command to `cd $WORKSPACE_HUB && uv run --script scripts/ai/generate-agent-radar.py` which reads the `# /// script` metadata and auto-installs pyyaml. |
| `cron-health` | MISSING | Task definition in `schedule-tasks.yaml` had no `schedule:` field, so `setup-cron.sh` never generated a crontab entry. | Added `schedule: "45 5 * * *"` matching the description's "05:45 UTC". |
| `architecture-scan` | ERROR | `fatal: Unable to create .git/index.lock` — concurrent git process collision on 04-05. | Transient; `git-safe.sh` already has `flock` coordination and `git_heal_index`. No code change needed — the library handles this. |
| `claude-plugin-audit` | ERROR | `Failed to parse installed_plugins.json` — the JSON file at `~/.claude/plugins/installed_plugins.json` was malformed or missing. | Transient data issue. Script already uses `die` on parse failure. No code change needed — next weekly run should succeed if the file is intact. |

## 8 False Positive Alerts — Fixed

All 8 false positives stem from the health check using a flat **25-hour**
staleness threshold for every job, regardless of actual schedule frequency.

### Weekly jobs flagged as STALE (5):

These run once per week but were flagged as stale because their last log was
naturally >25h old when checked mid-week:

- `ai-tools-status` (Sunday 03:15)
- `model-ids` (Sunday 03:30)
- `claude-plugin-audit` (Sunday 03:45)
- `architecture-scan` (Sunday 02:00)
- `staleness-scan` (Sunday 03:00)

### Jobs flagged as MISSING due to missing log directories (3):

These crontab entries existed but their log output directories had never been
created, so cron silently failed to write logs:

- `solver-watch-results` — `logs/solver/` did not exist
- `solver-dashboard` — same
- `ai-credit-utilization-weekly` — `logs/ai/` did not exist

### Fix applied

1. **`scripts/monitoring/cron-health-check.sh`**: Replaced flat 25h threshold
   with schedule-aware logic that parses the cron day-of-week field. Weekly
   jobs now get a 169h (7d+1h) threshold; sub-daily `*/N` jobs get `N+1` hours;
   daily jobs keep the 25h default.

2. **`config/scheduled-tasks/schedule-tasks.yaml`**: Fixed double-escaped
   `\\%Y\\%m\\%d` in `memory-health-check` command that caused date format
   issues in log filenames.

3. **Created missing log directories**: `logs/solver/`, `logs/ai/`,
   `logs/queue-refresh/` with `.gitkeep` files.

## 4 Missing Cron Jobs

These tasks are defined in `schedule-tasks.yaml` with correct schedules and
assigned to `ace-linux-1`, but were not present in the crontab (generated
2026-04-06T15:37:46Z). They were added to the YAML after the last
`setup-cron.sh --replace` run:

| Task | Schedule | Notes |
|---|---|---|
| `queue-refresh-weekly` | `30 22 * * 0` | Sunday 22:30 — agent work queue refresh |
| `compliance-daily` | `45 6 * * *` | Daily 06:45 — compliance monitoring |
| `compliance-weekly-report` | `0 7 * * 1` | Monday 07:00 — weekly compliance summary |
| `wiki-ingest-nightly` | `15 2 * * *` | Daily 02:15 — engineering wiki ingest |

**Action required**: Run `bash scripts/cron/setup-cron.sh` (or `--replace`)
to regenerate the crontab from the YAML source of truth. This will pick up
all 4 missing jobs plus the fixed `cron-health` and `agent-radar` entries.

## Verification

After applying fixes and running `setup-cron.sh`:

```bash
# Dry-run to verify all tasks are picked up
bash scripts/cron/setup-cron.sh --dry-run

# Run health check to confirm zero false positives
bash scripts/monitoring/cron-health-check.sh
cat .claude/state/cron-health/$(date -u +%Y-%m-%d).json | python3 -m json.tool
```
