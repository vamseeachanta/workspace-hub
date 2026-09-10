# Windows-native ecosystem scripts

Windows hosts (ace-win-1, ace-win-2) can't reliably run the bash ecosystem drivers directly:
a bare `bash` launch hangs (the WSL stub shadows Git Bash; stale PATH / UNC cwd stalls startup),
and the agent Bash tool inherits that hang. These PowerShell scripts are the **OS-appropriate
launchers** — they resolve the *real* Git Bash (MSYS/MINGW, never the WSL stub) where a bash
driver is canonical, or reimplement the thin compute layer in PowerShell where bash can't read
the hardware. The bash `.sh` files stay the single source of truth for logic; keep the pairs in
sync when either side changes.

## OS pairs

| Operation | Linux (canonical) | Windows |
|---|---|---|
| Sync all repos | `scripts/sync/sync-ecosystem.sh` | `scripts/sync/sync-ecosystem.ps1` |
| Reconcile ecosystem + equality | `scripts/readiness/reconcile-ecosystem.sh` | `scripts/windows/reconcile-ecosystem.ps1` (wraps the .sh via real Git Bash) |
| Equality collect + matrix | `scripts/readiness/equality-matrix-cron.sh` | `scripts/windows/equality-report.ps1` → `scripts/readiness/collect-equality.ps1` (CIM overlay) → `collect-equality.sh` |
| Equivalence sentinel | `scripts/monitoring/equivalence-sentinel.sh` | `scripts/windows/equivalence-sentinel.ps1` (wraps the .sh via real Git Bash) |
| Inbound SSH provisioning | *(n/a — Linux hosts already reachable)* | `scripts/windows/enable-remote-exec.ps1` (Windows-only; see below) |

Run pattern (note the `--` before bash-style flags so PowerShell passes them through):

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1            # read-only plan
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1 -- --apply # safe subset
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\equality-report.ps1                # refresh this box's column
```

## Durable job dispatch (`dispatch-run.ps1`)

**Windows OpenSSH kills the whole descendant process tree when the SSH session closes.**
Measured on a live host 2026-07-31: `cmd /c start /b` blocked the session on an inherited
handle *and* died at close; `Start-Process -WindowStyle Hidden` returned a PID in 1 s but the
process was already gone and its redirect files were 0 bytes. Neither survives. So nothing
long-running could be dispatched over plain SSH, which nullified the box's actual asset
(64 cores, free AQWA seats).

A Scheduled Task is the one mechanism proven durable here. `dispatch-run.ps1` wraps it in a
fire-and-forget interface. Every action emits a single JSON object, so a caller over SSH can
parse it directly.

```bash
# from the control surface. NOTE the forward slashes -- see the path trap below.
P='C:/path/to/workspace-hub/scripts/windows/dispatch-run.ps1'

ssh <host> "powershell -NoProfile -ExecutionPolicy Bypass -File '$P' \
  -Action submit -Shell bash -JobId myjob -Command 'long-running-thing.sh'"
ssh <host> "powershell ... -File '$P' -Action status  -JobId myjob"
ssh <host> "powershell ... -File '$P' -Action logs    -JobId myjob"
ssh <host> "powershell ... -File '$P' -Action list"
ssh <host> "powershell ... -File '$P' -Action cancel  -JobId myjob"
ssh <host> "powershell ... -File '$P' -Action cleanup -JobId myjob"   # deletes logs too
```

Verified end-to-end on a live host: submitted a 20-second job, the SSH session closed, the job
ran to completion detached, and a later session read back `state=finished`, `exit_code=5`, and
the captured stdout.

Notes that cost real debugging time:

- **Forward slashes in the `-File` path.** Once `DefaultShell` is Git Bash, bash eats the
  backslashes before PowerShell sees them (`C:\Users\...` arrives as `C:Users...`). PowerShell
  accepts `/` happily.
- **`schtasks` writes to stderr on success** ("trigger start time is in the past"), and under
  `$ErrorActionPreference='Stop'` PowerShell promotes *any* native stderr write to a terminating
  error. Native calls are judged by `$LASTEXITCODE` instead.
- **The runner-recorded `exit_code` is authoritative, not the task's `LastTaskResult`** — the
  latter reports whether the task *launched*, which is 0 for a successfully started job whose
  payload later failed. Both are reported so they can be compared.
- **No `/rl HIGHEST`.** Ordinary compute does not need elevation, and requiring it would force
  dispatch through an admin session.
- Tasks live under `\WorkspaceHubDispatch\` so they can never be confused with, or collide with,
  the licensed-run agent's task.
- **`cleanup` deletes the logs.** Fetch them first.

## Inbound SSH provisioning (`enable-remote-exec.ps1`)

Windows hosts sit in `manual_hosts` in [`config/fleet-ssh-hosts.yml`](../../config/fleet-ssh-hosts.yml),
so fleet automation cannot reach them and their state drifts unobserved — the 2026-07-30 fleet
sweep covered 3 of 5 machines, and one Windows host's equality evidence was 11.8 days stale
before anyone noticed. This script closes the reachability half of that gap (workspace-hub#3721).

**Audit-first, like `rdp-microphone.ps1`.** The default run mutates nothing and does not need
admin — it reports identity, SSH state, firewall exposure, and the poller's condition, then
writes an evidence JSON. Read that before applying: one of the two Windows hosts already has a
working SSH service, and which physical machine each fleet token denotes is still being settled
(deckhand#579, deckhand#581), so the script *reports* identity rather than assuming it.

```
:: audit — safe, non-admin, changes nothing
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1

:: provision — ELEVATED PowerShell required
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\enable-remote-exec.ps1 -Apply -PublicKey "ssh-ed25519 AAAA... operator@ace-linux-1"
```

Every apply step is idempotent. Three things it handles that are easy to get wrong by hand:

- **Administrator keys live elsewhere.** sshd reads `%ProgramData%\ssh\administrators_authorized_keys`
  for any account in the local Administrators group — not `%USERPROFILE%\.ssh\authorized_keys` —
  and ignores it unless the ACL is Administrators + SYSTEM only. The failure looks like a bad key
  but is a permission error.
- **The firewall rule is scoped** to the tailnet CGNAT range (`100.64.0.0/10`) by default, and the
  audit reports any *other* enabled rule already opening 22 so an unscoped exposure is visible.
- **Exit codes, not just output.** The fleet helpers branch on exit status, and a wrong default
  shell can return correct stdout while losing the exit code — which reads as success. Verify with
  `ssh <host> "exit 7"; echo $?` and require `7`.

It never starts or stops the licensed-run poller: whether that *should* run on a given host is
deckhand#579's decision, so the script only reports its state.

Full operator walkthrough: [`docs/runbooks/windows-remote-exec.md`](../../docs/runbooks/windows-remote-exec.md).

## RDP microphone audit and repair

`rdp-microphone.ps1` is a two-ended, audit-first tool for microphone redirection.
Run `-Role Client` on the workstation owning the microphone and `-Role Server` inside
the remote session. Repairs are limited to an explicit `.rdp` capture property or an
exact, checksummed target-consent reset/restore; privacy and machine policy are never
written. See `docs/runbooks/windows-rdp-microphone.md`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -TargetHost <remote-session-host> -OutputFormat Human
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Server -OutputFormat Human
```

Install the Windows machine-equivalence schedules from Git Bash:

```bash
# Preview using a test-only identity seam, then install using physical host identity.
bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-1 --what-if
bash scripts/windows/schedule-equivalence-tasks.sh
```

The installer is idempotent and registers four jobs from the canonical schedule
configuration: daily report-only reconciliation at 05:15, the equivalence sentinel every
six hours at minute 17, session curation every six hours at minute 47, and the weekly
equality report. `--machine` is intentionally accepted only with `--what-if`; live installs
derive the physical hostname and never trust `RECONCILE_MACHINE` for scheduler mutation.

Verify or remove the materialized tasks from PowerShell:

```powershell
Get-ScheduledTask -TaskPath '\Claude\' | Where-Object TaskName -in @(
  'EcosystemReconcile', 'EquivalenceSentinel', 'SessionCuration', 'EqualityReport'
)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\setup-scheduler-tasks.ps1 `
  -WorkspaceRoot (Get-Location).Path -EquivalenceOnly -Remove
```

Use `-WhatIf` on the removal command to preview it without querying or changing Task
Scheduler. Actual installation and one-shot sentinel validation must run from a clean,
current canonical checkout after merge.

## Host gotchas (ace-win-2, observed 2026-06)

- **`python3` is the Microsoft Store stub** (prints an install message, exits non-zero); **`python`
  is real**. `reconcile-ecosystem.sh` now probes for a working interpreter (prefers `python3`, falls
  back to `python`) so the worktree branch-guard runs on Windows. If you add python calls, do the same.
- **`equality-report.ps1` can die under PowerShell 5.1** in `Clear-GeneratedMatrixReport`
  (`git ls-files --error-unmatch … *> $null` → native stderr becomes a terminating error). The
  collect + matrix build succeed first; if it dies before commit, publish state-only by committing
  `.claude/state/equality-<machine>.yaml` manually (the Linux cron owns the published matrix HTML).
- **Peer push-race**: ecosystem pushes frequently collide; the drivers fetch + rebase + retry.

## Deprecated

- `git_all_repos.ps1` — legacy, hardcodes `C:\Users\vamseea\github` + `daily_routine.bat`;
  superseded by `scripts/sync/sync-ecosystem.ps1`. Kept only until any scheduled task referencing
  it is repointed.
