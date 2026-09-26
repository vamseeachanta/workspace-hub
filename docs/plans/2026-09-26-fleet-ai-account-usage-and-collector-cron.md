# Fleet AI-account usage sharing, and what else the collector VM should run

- **Date:** 2026-09-26
- **Status:** implemented (usage collector); decision register open (collector cron candidates)
- **Owner ask:** "we have 2 claude accounts and 2 codex accounts; communicate this and their usage to all repo-ecosystem machines; maximize usage where possible" — then "create a suitable cron job on the collector VM" — then "review the repo and machine ecosystem for further cron jobs the collector VM can take".
- **Owner context:** the company workstations carry one professional colleague seat (fewer authorisations); `ace-linux-1` carries the owner's personal seat (more authorisations). Harness upkeep (connect, run status, is the machine online, are the AI CLIs current, stale branches/worktrees without losing finished-session work) has fallen from ~90% of the owner's time a year ago to under 10% since Opus 5.5; the collector VM exists to push that remaining 10% to zero.

## 1. What changed

### Per-account usage, published fleet-wide

| Piece | Path | Role |
|---|---|---|
| Account map | `config/ai-tools/ai-accounts.yaml` | 4 accounts (label, provider, holder role, access, fingerprint) and which host is logged in as which. Public-safe: labels and hashes only. |
| Per-host probe | `scripts/ai/assessment/collect-account-usage.py` | Stdlib-only. Claude: OAuth usage endpoint with the host's Claude Code token (five_hour / seven_day / model buckets). Codex: `codex app-server` `account/rateLimits/read`, session-log fallback. Prints fingerprints (SHA-256 of the login, 12 hex), never tokens or addresses. Pipeable over ssh stdin. |
| Fleet fan-out + aggregate | `scripts/fleet/collect_account_usage_fleet.py` | ssh to every host (alias = fleet label), group samples by account, freshest wins, warn on fingerprint drift, emit `recommendation.<provider>` (account with most weekly headroom + the hosts that hold it). |
| Published aggregate | `config/ai-tools/account-usage-latest.json`, `docs/reports/ai-account-usage.md` | What every machine and agent reads. Hourly, commit-if-changed, `[skip ci]`. |
| Cron wrapper | `scripts/fleet/account-usage-cron.sh` | ff-only pull, collect, commit only the two files, push with one rebase retry. Never resets or discards. |
| Installer (collector VM) | `scripts/fleet/install-fleet-collector-cron.sh` | Checks PyYAML, origin push, ssh BatchMode reachability per host; installs the marked crontab line `7 * * * *`; `--run` does a first pass. |
| Routing rule | `.claude/rules/model-routing.md` | "Account headroom" paragraph: read the recommendation before marathons/dispatch, label `machine:<host>`. |
| Codex 0.157 fix | `scripts/ai/assessment/query-codex-usage.sh` | Weekly window is now `primary` with `windowDurationMins 10080`, `secondary` null; classify by window length. The old jq rejected every payload, so the statusline had been falling back to "manual" (0%). |

### Why per account, not per machine

A subscription's five-hour and weekly windows are counted against the account, wherever it is used. Two hosts logged in as the same seat see one budget. So the useful question is not "how much has this machine used" but "which seat has headroom, and which machines can run it". The aggregate answers exactly that, and the routing rule turns it into a `machine:` label.

### Verified on `ace-win-2` (2026-09-26 12:20 UTC)

- Claude probe: `source: oauth-api`, tier `default_claude_max_20x`, five_hour 34% used, seven_day 9% used, resets 2026-10-03. (The professional seat is a Max 20x plan.)
- Codex app-server: answers with `planType: pro`, weekly 8% used (10080-minute window as `primary`). The existing script and the first probe draft both read `secondary` and reported nothing — fixed as above.
- Tests: `tests/fleet/test_account_usage_fleet.py` (aggregation, recommendation, staleness, fingerprint drift, secret-free probe output).

### Assumptions to confirm (edit `ai-accounts.yaml`)

1. `ace-linux-2`, `gpu-claw` and the collector VM are logged in as the owner's seats (only `ace-linux-1` was stated). The first run prints each host's fingerprints; paste them into the `fingerprint:` fields and the aggregate will flag any host that is logged in as a different seat.
2. Codex is logged in on both Windows workstations and on `ace-linux-1`/`ace-linux-2` (the registry's `agent_clis` is stale and says otherwise). A host without `auth.json` reports `unavailable` and is simply skipped.
3. The collector's `~/.ssh/config` has `Host <label>` entries for `ace-linux-1`, `ace-linux-2`, `gpu-claw`, `ace-win-1`, `ace-win-2` (it already reaches them for the daily snapshot).

## 2. Installing the collector cron

On the collector VM, from its `workspace-hub` checkout (currently on `pilot/idea-compass-links`, 14 behind — switch to `main` first):

```bash
git switch main && git pull --ff-only
bash scripts/fleet/install-fleet-collector-cron.sh --check   # prerequisites + reachability
bash scripts/fleet/install-fleet-collector-cron.sh --run     # install crontab line, run once
cat docs/reports/ai-account-usage.md                          # fingerprints per host
```

Catalogue note: `config/scheduled-tasks/schedule-tasks.yaml` is the single source of truth and requires the host to be in `config/workstations/registry.yaml`; both files sit under the scheduler mutation attestation (#3475). The collector VM is not registered yet, so this job is installed directly, exactly as the existing daily `fleet-daily-collector` is. Registering `fleet-collector` and moving both jobs into the catalogue is item D1 below.

## 3. Decision register: further cron jobs for the collector VM

Source: full read of `schedule-tasks.yaml` (67 tasks), the Windows scheduler installer, the registry, the control-surface skill and open fleet issues. The collector VM has ssh to the whole fleet, a checkout, `gh`; it has no licensed solver, no GPU, no Windows, no Outlook, and no session logs of its own.

**Rule that shapes every row:** a job moves only if the *data* it works on is in git/GitHub or reachable over ssh. Per-box self-report and self-repair jobs stay where the box is. Anything that mutates GitHub (creates issues, comments, labels) collides with the "ace-linux-1 is the single dispatch surface" policy (#3497, control-surface skill) and needs an explicit owner decision.

### Tier A — add now (new fleet jobs; nothing exists today, no policy conflict)

| # | Job | Cadence | What it does | Why the collector | Human decision |
|---|---|---|---|---|---|
| A1 | **AI account usage** | hourly | this PR | account windows are global; one prober is enough | done |
| A2 | **Fleet hygiene alerts** (#3499) | every 6 h | from the daily snapshot fields it already gathers (`behind`, `ahead`, `dirty`, `branch`), raise a threshold alert (behind > 10, dirty > 50, not on main) as a comment on #3499 or a `docs/reports/fleet-alerts.md` line | the snapshot is already collected here; no alerting exists | ☐ report-only file (recommended) / issue comment |
| A3 | **AI CLI version parity** | daily | ssh `claude --version`, `codex --version`, `gemini --version`, `uv --version` per host vs the newest seen; publish `docs/reports/fleet-cli-versions.md`; flag hosts > 1 minor behind | "is the AI software up to date" is one of the owner's residual chores; `ai-tools-status` runs only on ace-linux-1 and is a self-report | ☐ report-only (recommended) / also run `harness-update` remotely |
| A4 | **Stale branch + worktree sweep, report-only** | daily | per host over ssh: `git worktree list`, branches merged into origin/main, stashes; publish a per-host table with the *safe* command for each (never executes; the `reconcile-ecosystem` skill's guard rules apply) | `merge-cleanup.md` names `scripts/operations/merge-cleanup-sweep.sh` as the target and the file does not exist; the reconcile skill runs per box only | ☐ report-only first (recommended); execution stays per box |
| A5 | **Fleet cron health** | daily | ssh `crontab -l` + newest log mtime per declared task on each Linux host; Windows via `schtasks /query` (Git Bash shell); flag tasks that have not written a log in 2× their period | `cron-health` reads only local logs; #1512 closed without a fleet view | ☐ add |
| A6 | **Unpushable-commit detector** (#3705) | every 6 h | from snapshot `ahead > 0` on protected `main`, list the stranded commits per host | no fleet-level detection exists | ☐ add (cheap: reuses A2 data) |

### Tier B — move from ace-linux-1 (repo-only jobs; remove from a1 in the same change, never duplicate)

| # | Task (schedule-tasks.yaml) | Cadence | Needs | Human decision |
|---|---|---|---|---|
| B1 | `research-staleness` | daily | repo only | ☐ move |
| B2 | `doc-drift`, `agent-radar`, `tier1-indexing-freshness`, `memory-health-check`, `flywheel-review`, `harness-lean-out`, `skills-curation`, `model-ids` | daily / weekly | repo only, commit+push | ☐ move as one batch |
| B3 | `architecture-scan`, `staleness-scan` | weekly | repo only, commit+push | ☐ move |
| B4 | `solver-watch-results`, `solver-dashboard` | 4 h / daily | polls a git queue; no solver | ☐ move |
| B5 | `session-analysis` | daily | reads `.claude/state/session-signals` after `git pull` (signals arrive via git) | ☐ move |
| B6 | `equality-matrix-refresh` — build + publish half only | 6 h | origin evidence; it is the dead-man's switch, so single owner | ☐ move build/publish; keep collect on each box |
| B7 | `weekly-hermes-parity-review` | weekly | already an ssh fleet collector | ☐ move |
| B8 | `dep-health`, `gtm-job-market-scan` | daily / weekly | sibling repos cloned; miniforge/uv | ☐ move once the clones exist on the VM |
| B9 | `benchmark-regression` | daily | host-relative baseline: the number would change meaning | ☐ leave on a1 (recommended) |

### Tier C — move only with logins on the VM and an explicit control-surface exception

| # | Task | Why it is conditional |
|---|---|---|
| C1 | `gsd-researcher`, `daily-today` | need `claude -p` login on the VM (owner seat → counts against `claude-owner`) |
| C2 | `review-audit`, `compliance-daily` + `compliance-weekly-report`, `weekly-governance-check`, `gemini-nightly-batch`, `queue-refresh-weekly`, `consistency-weekly-check` | mutate GitHub; #3497 keeps that on ace-linux-1 unless failover is chosen. Single-owner constraints (consistency-weekly-check) mean remove-then-add. |
| C3 | `provider-utilization-refresh`, `ai-credit-utilization-weekly` | superseded by A1 for quota; the HOME-local weekly log would restart on the VM |
| C4 | `dispatch-leader-watch` as a **secondary** watcher; leader failover (#2847 phase 2) | the a1 run *is* the heartbeat; the VM could be the promotion authority when a1 is down — a design decision, not a cron move |
| C5 | `licensed-run-alarm` | needs the deckhand env and dedicated clones on the VM |

### Tier D — prerequisites and the "must not move" list

- **D1 Register the VM.** Add `fleet-collector` to `config/workstations/registry.yaml` (os linux, `schedule_variant: contribute`, role `fleet-collector`) and declare A1 + the daily snapshot in `schedule-tasks.yaml`; re-attest under #3475; then `setup-cron.sh` owns the VM's crontab and the direct-crontab installer is retired. Also fix `agent_clis` for the Linux boxes (codex is present) and add `ace-win-1`'s real hostname alias privately, not in the public file.
- **D2 Put the VM's checkout on `main`.** It is on `pilot/idea-compass-links`, 14 behind (snapshot 2026-09-26). Every job above assumes `main`.
- **Must not move:** licensed solver runs (FlexNet needs an interactive logon; ace-win-1 is shared tenancy); every per-box self-report/self-repair job (equality collect, equivalence-sentinel, session-curation, harness-checkup, harness-install-doctor, harness-update, git-lock-reaper, return-to-main-guard, parity-sentinel, dream/Hermes bridges, quota-snapshot-refresh, claude-plugin-audit, cron-health local, repo-ecosystem-hygiene, all repository-sync variants, all `win-*` tasks); local data mounts (`drive-index-*` on /mnt/ace, /mnt/dde); HOME-resident state (agent-memory-backup, email-queue-*, memory-health-report, session exports); `dispatch-pull` and the leader heartbeat.

### Recommendation

Do A1 (done) → D2 → A2 + A6 (one script, reads the snapshot the VM already has) → A3 → A5 → A4 report-only. Then B1–B7 as one PR that deletes the a1 entries and adds `fleet-collector` entries under D1. Leave Tier C until the owner decides whether the VM may hold seats and mutate GitHub.

## Decision to request

1. Confirm the seat-to-host map in `ai-accounts.yaml` (assumptions 1–3 above) and paste the fingerprints after the first run.
2. Approve Tier A as report-only jobs on the collector VM (A2–A6), and D1/D2 as the prerequisite PR.
3. Decide Tier B batch move (remove from ace-linux-1, add to the VM), and whether B9 stays.
4. Decide whether the VM may hold AI seats (Tier C1/C3) and mutate GitHub (Tier C2/C4) — this is the #3497 control-surface exception.
