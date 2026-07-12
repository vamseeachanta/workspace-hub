# Scheduled Tasks Inventory

> Source of truth: `config/scheduled-tasks/schedule-tasks.yaml`
> Installer: `scripts/cron/setup-cron.sh` (compatibility wrapper over the transactional `cron_apply.py` engine)
> Validator: `scripts/cron/validate-schedule.py`

## Mutation Safety Audit

Scheduler mutation ownership is cataloged separately from task cadence in
`config/scheduled-tasks/mutation-surfaces.yaml`. The registry covers direct
cron, systemd-user, and Windows Task Scheduler writers plus reviewed transitive
entrypoints. Its checker derives status from tracked index bytes and does not
authorize live scheduler changes.

Direct cron ownership is restricted to canonical and declared legacy exact
lines. Transitive entrypoints declare their complete delegation chain,
terminal operation, mode arguments, target, exit behavior, and source
attestation. The onboarding preview gap remains visible as
[#3490](https://github.com/vamseeachanta/workspace-hub/issues/3490), while the
harness-update error-swallowing disposition remains #3479.

```bash
# Validate inventory, source attestations, and dispositions
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py

# Verify the deterministic exact-identity inventory
uv run python scripts/cron/build-cron-identity-inventory.py --check

# Verify the committed human audit is byte-current
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py \
  --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
```

The human audit records [#3475](https://github.com/vamseeachanta/workspace-hub/issues/3475)
as resolved and links active migration issues
[#3476](https://github.com/vamseeachanta/workspace-hub/issues/3476) through
[#3479](https://github.com/vamseeachanta/workspace-hub/issues/3479). Issue
coordinates are checked offline; their live state is informational and does
not convert a `migration-required` row into compliance.

### Scheduler identity and host binding

- `current-user-cron` is the crontab owned by the invoking local user.
- `root-cron` is the local root crontab and requires explicit root execution.
- `systemd-user` is the invoking user's local systemd manager and unit namespace.
- `windows-current-user-task` is the current Windows user's Task Scheduler namespace.
- `physical-local` binds mutation to the physical host running the writer, not a machine alias or workspace path.
- `explicit-remote-transport` is required for intentional mutation through a declared remote transport; remote targeting must never be inferred.

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
| 04:25 daily | hermes-claude-bridge | Hermes → Claude repo-memory bridge; staggered on ace-linux-1 and invoked as `bridge-hermes-claude.sh --commit` | `logs/orchestrator/memory-bridge/hermes-claude-*.log` |
| 05:00 daily | claude-memory-backup | rsync memory to dev-secondary | `/tmp/claude-memory-backup.log` |
| 05:35 daily | repo-ecosystem-hygiene | Read-only repo ecosystem hygiene audit; writes ignored local Markdown/JSON state | `logs/quality/repo-ecosystem-hygiene-*.log` |
| 05:45 daily | cron-health | Scheduled-task log freshness/error scan | `logs/quality/cron-health-*.log` |
| 05:57 daily | email-queue-attention-notify | PII-safe email attention route notification writer | `logs/email/queue-attention-notify-*.log` |
| 06:00 daily | daily-today | Daily productivity summary | `logs/daily/cron.log` |
| */4h | repository-sync | Pull/push all repos through the singleton runtime wrapper | `logs/repository-sync-*.log` |

## Task Schedule (ace-linux-2 / dev-secondary — contribute variant)

| Time | ID | Description | Log |
|------|-----|-------------|-----|
| 01:45 daily | harness-update | AI harness tools update (GStack, Hermes, Superpowers, GSD) | `logs/maintenance/harness-update-*.log` |
| */4h | repository-sync | Pull/push all repos through the singleton runtime wrapper | `logs/repository-sync-*.log` |

## Runtime Health Contract

Tasks may opt in through a `runtime:` mapping in
`config/scheduled-tasks/schedule-tasks.yaml`. `repository-sync` is the first
enforced singleton and uses a 10,800-second budget, which is below its four-hour
cadence. Its local state lives under
`.claude/state/cron-runtime/repository-sync/`.

Cron health keeps log and runtime evidence independent. Runtime status values
are:

- `never_started` — no lifecycle evidence exists;
- `active_within_budget` — the recorded child identity is live and within its budget;
- `completed_success` — the latest completed invocation exits zero;
- `completed_failure` — the latest completed invocation exits nonzero or by signal;
- `overlap` — a second invocation encounters the singleton owner;
- `filesystem_wait` — the recorded child reports process state `D` or an explicitly configured wait channel;
- `excessive_runtime` — the live child exceeds `max_seconds`;
- `stale_or_reused_pid` — the recorded child is absent or its start token differs;
- `orphan_contention`, `invalid_state`, and `unknown` — evidence is inconsistent or inspection cannot complete safely.

The runner stores `active.json`, `contention.json`, and `last-result.json`
separately so contention cannot overwrite owner or completion evidence. It
records the mutating child PID/PGID rather than treating the waiting supervisor
as the workload.

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

# Preview the fail-closed transaction against this user's live crontab
bash scripts/cron/setup-cron.sh --dry-run --machine ace-linux-1

# Install/update through backup + lock + compare-and-swap + rollback checks
bash scripts/cron/setup-cron.sh --machine ace-linux-1

# Preview fail-closed transactional reconciliation
uv run --script scripts/cron/cron_apply.py --machine ace-linux-1 --json

# Check current crontab
crontab -l
```

`setup-cron.sh` no longer has an independent append/fingerprint algorithm. Both
entrypoints use the same renderer, ownership classification, managed block, and
transaction. Preview may fail on an unknown live line; classify that ownership
instead of bypassing the abort. Applying while a communications daemon is live
also fails unless the operator explicitly supplies `--allow-live-reload` after
reviewing the preview.

`--machine` selects catalog/registry behavior but never targets another host's
crontab. Run the command on the machine whose local crontab is being reconciled.
Windows `contribute-minimal` targets print Task Scheduler guidance and do not
invoke Linux cron reconciliation.

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
