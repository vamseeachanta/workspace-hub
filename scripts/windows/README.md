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

Run pattern (note the `--` before bash-style flags so PowerShell passes them through):

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1            # read-only plan
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1 -- --apply # safe subset
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\equality-report.ps1                # refresh this box's column
```

Install the Windows machine-equivalence schedules from Git Bash:

```bash
# Preview, then install the three equivalence-only tasks.
bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-1 --what-if
bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-1
```

The installer is idempotent and registers daily report-only reconciliation, six-hour
session curation, and the weekly equality report from the canonical schedule configuration.

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
