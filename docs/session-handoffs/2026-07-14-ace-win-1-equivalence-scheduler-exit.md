# ace-win-1 machine-equivalence scheduler exit handoff

Date: 2026-07-14  
Machine identity: `ace-win-1`  
Workspace: `D:\ws\workspace-hub`

## Outcome

Machine-equivalence collection, reporting, and reconciliation are installed in
Windows Task Scheduler under `\Claude\`. The scheduler installer is idempotent,
uses the repository's public machine identity, and keeps the daily ecosystem
reconcile job in report-only mode. The machine-equality matrix and evidence were
regenerated and published during live validation.

## Installed tasks and verified state

| Task | Schedule | Last verified result | Next run at exit |
|---|---|---:|---|
| `SessionCuration` | Every 6 hours at minute 47 | `0` at 2026-07-14 14:01 | 2026-07-14 18:47 |
| `EcosystemReconcile` | Daily at 05:15 | `0` at 2026-07-14 14:01 | 2026-07-15 05:15 |
| `EqualityReport` | Weekly Monday at 04:30 | `0` at 2026-07-14 14:02 | 2026-07-20 04:30 |

All three tasks were `Ready` after their successful validation runs. The first
scheduled curation run after reinstall initially failed its repository freshness
guard because the checkout was 31 commits behind upstream. The checkout was
fast-forwarded and all three tasks were then rerun successfully.

## Operator commands

Install or refresh the three tasks from Git Bash:

```bash
cd /d/ws/workspace-hub
bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-1
```

Preview registration without changing Task Scheduler:

```bash
bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-1 --what-if
```

Verify task state and results from PowerShell:

```powershell
Get-ScheduledTask -TaskPath '\Claude\' |
  Where-Object TaskName -in 'EqualityReport','SessionCuration','EcosystemReconcile' |
  Select-Object TaskName, State

Get-ScheduledTaskInfo -TaskName 'EcosystemReconcile' -TaskPath '\Claude\' |
  Select-Object LastRunTime, LastTaskResult, NextRunTime
```

Run one task immediately:

```powershell
Start-ScheduledTask -TaskName 'EcosystemReconcile' -TaskPath '\Claude\'
```

## Safety and observability

- `EcosystemReconcile` runs daily without `--apply`; it produces findings but
  does not make unattended ecosystem changes.
- The public label `ace-win-1` is passed to collectors and wrappers so generated
  evidence, logs, and future commit subjects do not use the private OS hostname.
- Daily reconcile output is written to
  `logs/quality/reconcile-ace-win-1-YYYY-MM-DD.log`.
- The latest validated log is
  `logs/quality/reconcile-ace-win-1-2026-07-14.log`.
- A previously published validation commit (`bc99db944`) has the private OS
  hostname in its subject. Its evidence content is sanitized, shared history was
  not rewritten, and recurrence was fixed by `9a09da2fe`.

## Implementation record

- `5980b3063` - schedule machine-equivalence reconciliation and repair Windows
  scheduler/collector behavior.
- `e1c04317b` - prevent curation matrix previews from dirtying the equality guard.
- `9927b5e34` - resolve Git Bash reliably from the equality collector.
- `9a09da2fe` - use the public machine label in equality publication.
- `03cc01e0c` - label reconcile logs with the public machine identity.
- `2c42085bc` - add the Git Bash scheduling wrapper.
- `4cd17564c` - latest successful equality report published from `ace-win-1`.

Relevant validation completed during implementation: 109 readiness tests, 14
scheduler-contract tests, shell syntax validation, wrapper preview, live task
registration, and successful manual execution of every installed task.

## Preserved local state

The tracked checkout was synchronized with `origin/main` at exit. Seven generated
curation state files remain untracked and were intentionally preserved:

```text
.claude/state/memory-freshness-ace-win-1.json
.claude/state/session-curation-ace-win-1.json
.claude/state/session-curation-digest-ace-win-1.md
.claude/state/skill-currency-ace-win-1.json
.claude/state/skill-drift-ace-win-1.json
.claude/state/skill-drift-report-ace-win-1.json
.claude/state/skill-link-health-ace-win-1.json
```

`stash@{0}` is an older autostash and was left untouched because its ownership
and continued value were not established.

## Follow-up

After the next unattended daily reconcile, verify that `LastTaskResult` remains
`0` and review the dated reconcile log. Reconcile findings that require changes
should continue through a reviewed/manual apply workflow rather than enabling
unattended `--apply`.
