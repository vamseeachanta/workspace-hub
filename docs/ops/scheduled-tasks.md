# Scheduled Tasks Inventory

> Source of truth: `config/scheduled-tasks/schedule-tasks.yaml`
> Installer: `scripts/cron/setup-cron.sh`
> Validator: `scripts/cron/validate-schedule.py`

## Machine Roles

| Hostname | Aliases | Cron Variant | Scheduler |
|----------|---------|-------------|-----------|
| ace-linux-1 | dev-primary, vamsee-linux1 | full | cron |
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
| 04:00 Mon | skills-curation | Weekly skills curation v2: duplicate names, leaf collisions, wrapper pairs, and filesystem-only active skill loss-risk inventory (local-only JSON + Markdown artifacts) | `logs/maintenance/skills-curation-*.log` |
| 04:30 Mon | weekly-hermes-parity-review | Hermes cross-machine parity review | `logs/weekly-parity/cron-*.log` |
| 04:30 daily | notification-purge | Delete notification JSONL > 7 days | — |
| 05:00 daily | claude-memory-backup | rsync memory to dev-secondary | `/tmp/claude-memory-backup.log` |
| 05:35 daily | repo-ecosystem-hygiene | Read-only repo ecosystem hygiene audit; writes ignored local Markdown/JSON state | `logs/quality/repo-ecosystem-hygiene-*.log` |
| 05:45 daily | cron-health | Scheduled-task log freshness/error scan | `logs/quality/cron-health-*.log` |
| 06:00 daily | daily-today | Daily productivity summary | `logs/daily/cron.log` |
| */4h | repository-sync | Pull/push all repos | `.claude/state/learning-reports/cron.log` |

## Task Schedule (ace-linux-2 / dev-secondary — contribute variant)

| Time | ID | Description | Log |
|------|-----|-------------|-----|
| 01:45 daily | harness-update | AI harness tools update (GStack, Hermes, Superpowers, GSD) | `logs/maintenance/harness-update-*.log` |
| */4h | repository-sync | Pull/push all repos | `.claude/state/learning-reports/cron.log` |

## Task Schedule (licensed-win-1 / licensed-win-2 - Windows Task Scheduler)

`scripts/windows/setup-scheduler-tasks.ps1` renders `\Claude\EqualityReport` from
`config/scheduled-tasks/schedule-tasks.yaml` instead of hardcoding a duplicate cadence.
The task runs `scripts/windows/equality-report.ps1`, which uses system `python` for the
matrix build and commits/pushes `.claude/state/equality-*.yaml` after a successful
collector + matrix run.

| Time | ID | Description | Log |
|------|-----|-------------|-----|
| 04:30 Mon | equality-report | Machine-equality self-report plus matrix build; commits/pushes equality state | `logs/quality/equality-*.log` |

## Skills Curation v2 Contract

The `skills-curation` scheduled task remains the single periodic path for skill ecosystem housekeeping. Its default cron invocation is local-only: it writes deterministic JSON and Markdown artifacts under `logs/maintenance/skills-curation/`, does not call `gh`, does not require network access, and does not mutate `.claude/skills` or `.claude/state/skill-usage-report/`. In v2 it also reports tracked-vs-filesystem inventory, including active filesystem-only `SKILL.md` files that are at risk of loss until dispositioned.

Optional manual operator support may render `github-update-payload.md` in the same audit output directory with `--render-github-payload`; that file is a local payload only and is not posted automatically.

## Repo Ecosystem Hygiene

The `repo-ecosystem-hygiene` task runs daily at 05:35 UTC on `dev-primary` / `ace-linux-1` before `cron-health`. It is read-only: it probes the workstation-registry repo universe, first-level sibling residue, historical registry entries, and selected scheduler health links, then writes ignored local state under `.claude/state/repo-ecosystem-hygiene/`.

Manual operator run:

```bash
UV_CACHE_DIR=.claude/state/uv-cache bash scripts/cron/repo-ecosystem-hygiene-audit.sh
```

Primary artifacts:

- `.claude/state/repo-ecosystem-hygiene/latest.md`
- `.claude/state/repo-ecosystem-hygiene/latest.json`
- `logs/quality/repo-ecosystem-hygiene-*.log`

The task exits 0 after a completed audit even when repo findings are `WARN` or `ERROR`; execution failures emit the `repo-ecosystem-hygiene execution_failed` marker so `cron-health` can catch broken automation separately from expected drift.

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

- `harness-update` added to ace-linux-2 (was ace-linux-1 only) — updates GStack, Hermes, Superpowers, GSD daily at 01:45
- Hermes config templates added to `config/agents/hermes/` — synced via `sync-agent-configs.sh`
- ace-linux-2 NVIDIA kernel module missing for 6.17.0-20 — tracked in #1581
- Hermes install on ace-linux-2 — tracked in #1582

## Audit Notes (2026-03-25)

- Hostname `ace-linux-1` added as alias for `dev-primary` in setup-cron.sh, comprehensive-learning.sh, validate-schedule.py
- `daily-today` task added (was never in crontab — daily logs stopped March 2)
- `agent-radar` PATH fix applied (12 consecutive failures due to missing `uv`)
- `session-analysis.sh` printf bugs fixed
- Notification JSONL (`logs/notifications/`) has no consumer — future work
