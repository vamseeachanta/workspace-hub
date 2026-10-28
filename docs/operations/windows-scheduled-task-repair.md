# Windows scheduled task actions

The installers resolve the repository root at installation, store absolute script
paths and a working directory, and invoke PowerShell with `-NoProfile -File`.
The shared runner starts shell scripts with the resolved Git Bash executable.
The context task uses the shell implementation directly; the batch file remains
an optional compatibility entry point. Existing task names and schedules remain.

## Reinstallation

On **each Windows installation**, open an administrator PowerShell console in the
updated repository root. Preview the definitions, then register them:

```powershell
powershell -NoProfile -File .\scripts\windows\setup-scheduler-tasks.ps1 -DryRun
powershell -NoProfile -File .\scripts\windows\setup-scheduler-tasks.ps1
```

The preview emits one JSON object per applicable task, including `Execute`,
`Arguments`, `ScriptPath`, `ScriptArguments`, `WorkingDirectory`, `Schedule`,
`LogPattern` and `LogPath`. It returns before constructing scheduler objects or
querying, registering or removing tasks. `-WhatIf` remains an alias-compatible
preview. An identity override remains restricted to previews. A missing Git Bash
is reported in the main preview and blocks live installation.

The context-only compatibility installer accepts the same `-DryRun` option and
uses the same action renderer. Full reinstallation above includes context, so
running both installers is unnecessary. Reinstall after moving the checkout or
Git Bash. Task execution uses the existing execution policy; policy refusal
requires the normal script trust or signing procedure.

## Task disposition

| Task | Disposition and reason | Output pattern, relative to the repository |
| --- | --- | --- |
| ContextManagementDaily | KEEP+FIX: run the shell implementation with the derived root; retain daily context reporting. | `logs/scheduler/ContextManagementDaily-*.log` |
| WorkstationVersionCheck | KEEP+FIX: absolute shell action; retain installed-version checks and preserve later daily-log sections. | `logs/scheduler/WorkstationVersionCheck-*.log` |
| NightlyReadiness | KEEP+FIX: retain daily readiness checks with a resolved action and captured output. | `logs/scheduler/NightlyReadiness-*.log` |
| RepoSync | KEEP+FIX: retain repository synchronization with a resolved action and captured output. | `logs/repository-sync-*.log` |
| MemoryBridgeSync | KEEP+FIX: retain the existing memory refresh arguments with a resolved action and captured output. | `logs/orchestrator/memory-bridge/hermes-claude-*.log` |
| HarnessUpdate | KEEP+FIX: retain existing updater behavior with a resolved action and captured output. | `logs/maintenance/update-harness-tools-*.log` |
| EqualityReport | KEEP+FIX: preserve the catalog schedule and freshness guards; remove execution-policy bypass. | `logs/quality/equality-*.log` |
| SessionCuration | KEEP+FIX: preserve the catalog schedule; isolate the collector's exit in a child process so curation can finish. | `logs/monitoring/session-curation-*.log` |
| EcosystemReconcile | KEEP+FIX: retain report-only behavior and the catalog schedule with a resolved action and captured output. | `logs/quality/reconcile-*.log` |
| RepoHygieneAutoSafe | KEEP+FIX: preserve conditional catalog selection and report-only behavior with a resolved action and captured output. | `logs/quality/repo-hygiene-auto-safe-*.log` |
| EquivalenceSentinel | KEEP+FIX: preserve the recurring interval and explicit wrapper arguments with captured output. | `logs/monitoring/equivalence-sentinel-*.log` |

There are **no RETIRE candidates for past fixed dates** in these two installers.
The `-Once` trigger computes its next start from the current date and repeats
at the configured interval; it is not an expired one-off task. Independent solver
queue and on-demand registration utilities are outside this repair.

## Logs and remaining diagnosis

Each invocation writes a timestamped UTF-8 log. Standard output, standard error,
and a final `OK:` or `ERROR:` exit marker are captured; the runner returns the
child status to Task Scheduler. Separate files prevent an earlier failure from
contaminating the next run's health scan. Catalog-backed jobs use their catalog
log patterns, which the cron health collector already reads. The three
installer-only jobs use `logs/scheduler/`; the current cron catalog does not grade
those jobs, so inspect their logs and Task Scheduler results directly. No new
catalog schedules or scheduler permissions are introduced.

These changes do not prove installed software, credentials, network access,
checkout freshness, or successful execution on Windows. Version checks continue
to fail for missing required installations. Equality freshness and dirty-state
guards continue to reject unsafe inputs. Existing publication behavior is
retained. A second-provider review and local Windows validation are required
before relying on the repaired registrations.

## Verification

The Linux regression suite is:

```bash
uv run --no-project --with pytest --with pyyaml python -m pytest tests/readiness/test_windows_task_actions.py tests/readiness/test_windows_scheduler_single_source.py -q -rA -p no:cacheprovider
```

PowerShell behavioral tests exercise preview output for both catalog Windows
configurations, block scheduler API calls, compare both installers, and run
only disposable child scripts to check quoting, stdout, stderr and exit codes:

```powershell
powershell -NoProfile -File .\tests\readiness\windows-task-actions.ps1 -ScratchDirectory (Join-Path $env:TEMP ('scheduler-tests-' + [guid]::NewGuid()))
```

The behavioral test never installs tasks. Its scratch directory must be fresh.
