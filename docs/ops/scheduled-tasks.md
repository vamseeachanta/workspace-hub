# Scheduled Tasks Inventory

> Source of truth: `config/scheduled-tasks/schedule-tasks.yaml`
> Installer: `scripts/cron/setup-cron.sh`
> Validator: `scripts/cron/validate-schedule.py`

## Machine Roles

| Hostname | Aliases | Cron Variant | Scheduler |
|----------|---------|-------------|-----------|
| ace-linux-1 | dev-primary | full | cron |
| ace-linux-2 | dev-secondary | contribute | cron |
| licensed-win-1 | — | contribute-minimal | Windows Task Scheduler |
| licensed-win-2 | — | contribute-minimal | Windows Task Scheduler |

## Task Schedule (ace-linux-1 / dev-primary — full variant)

| Time | ID | Description | Log |
|------|-----|-------------|-----|
| 01:15 daily | harness-update | AI harness tools update (GStack, Hermes, Superpowers, GSD) | `logs/maintenance/harness-update-*.log` |
| 01:00 daily | dep-health | Dependency health + CVE check | `logs/quality/dep-health-cron.log` |
| 01:30 daily | benchmark-regression | Performance benchmark regression | `logs/quality/benchmark-*.log` |
| 02:00 daily | comprehensive-learning | 10-phase nightly learning pipeline | `.claude/state/learning-reports/cron.log` |
| 02:30 daily | doc-drift | Documentation drift baseline | `logs/quality/doc-drift-*.yaml` |
| 02:30 daily | agent-radar | Agent capability radar HTML | `/tmp/agent-radar.log` |
| 03:15 Sun | ai-tools-status | AI CLI version audit | `.claude/state/learning-reports/cron.log` |
| 03:30 Sun | model-ids | Model ID refresh | `.claude/state/learning-reports/cron.log` |
| 04:00 Mon | skills-curation | Skill eval + duplicate detect | `.claude/state/learning-reports/cron.log` |
| 04:30 Mon | weekly-hermes-parity-review | Hermes cross-machine parity review | `logs/weekly-parity/cron-*.log` |
| 04:30 daily | notification-purge | Delete notification JSONL > 7 days | — |
| 05:00 daily | claude-memory-backup | rsync memory to dev-secondary | `/tmp/claude-memory-backup.log` |
| 06:00 daily | daily-today | Daily productivity summary | `logs/daily/cron.log` |
| */4h | repository-sync | Pull/push all repos | `.claude/state/learning-reports/cron.log` |

## Task Schedule (ace-linux-2 / dev-secondary — contribute variant)

| Time | ID | Description | Log |
|------|-----|-------------|-----|
| 01:15 daily | harness-update | AI harness tools update (GStack, Hermes, Superpowers, GSD) | `logs/maintenance/harness-update-*.log` |
| */4h | repository-sync | Pull/push all repos | `.claude/state/learning-reports/cron.log` |

## Comprehensive Learning Sub-Steps (02:00)

The `comprehensive-learning` cron entry runs `comprehensive-learning-nightly.sh` which orchestrates:

1. `git pull` — aggregate contributions
2. rsync sessions from dev-secondary, licensed-win-1
3. Portfolio signals update
4. AI agent readiness check
5. Release notes scan (+ auto-commit new WRK items)
6. Skill frontmatter validation
7. Skill curation (if nightly script exists)
8. Nightly readiness checks
9. Test health check
10. Provider cost tracking
11. Specs index rebuild
12. Codex drift scan
13. Main 10-phase pipeline (`comprehensive-learning.sh`)
14. Notification via `notify.sh`

## Operations

```bash
# Validate YAML
uv run --no-project python scripts/cron/validate-schedule.py

# Preview what would be installed
bash scripts/cron/setup-cron.sh --dry-run

# Install/update crontab
bash scripts/cron/setup-cron.sh

# Check current crontab
crontab -l
```

## Audit Notes (2026-04-01)

- `harness-update` added to ace-linux-2 (was ace-linux-1 only) — updates GStack, Hermes, Superpowers, GSD daily at 01:15
- Hermes config templates added to `config/agents/hermes/` — synced via `sync-agent-configs.sh`
- ace-linux-2 NVIDIA kernel module missing for 6.17.0-20 — tracked in #1581
- Hermes install on ace-linux-2 — tracked in #1582

## Audit Notes (2026-03-25)

- Hostname `ace-linux-1` added as alias for `dev-primary` in setup-cron.sh, comprehensive-learning.sh, validate-schedule.py
- `daily-today` task added (was never in crontab — daily logs stopped March 2)
- `agent-radar` PATH fix applied (12 consecutive failures due to missing `uv`)
- `session-analysis.sh` printf bugs fixed
- Notification JSONL (`logs/notifications/`) has no consumer — future work
