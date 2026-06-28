# Windows / no-SSH host cutover (epic #2998)

> Operator runbook — run **on the host** in **Git Bash** (these hosts have `ssh: null`, so there is no
> remote cutover). Covers WF1 (#2999 reconciler), WF2/WF5a (#2815/#2816 equality scheduler + self-report),
> and WF3 (#3000 pull dispatch). Safe: the deny-list write is additive + backed up; the equality step is
> read-only compute + a scoped commit; the pull-dispatch step is dry-run. None of it touches OrcaFlex /
> AQWA / ANSYS runs.

## Run it

```bash
# === workspace-hub no-SSH Windows cutover (Git Bash on the host) ===
set -e
cd /d/workspace-hub
MACHINE=ace-win-1          # <-- set to ace-win-2 on the second host

# 0. Clean, current main (the equality wrapper refuses dirty/ahead/behind worktrees)
git fetch origin
git checkout main
git pull --ff-only
python -m pip install --user pyyaml        # uv is not installed on these hosts

# 1. WF1 #2999 — converge the safety deny-list into %USERPROFILE%\.claude\settings.json
python scripts/readiness/harness_reconcile.py --machine "$MACHINE"           # DRY-RUN: shows drift
python scripts/readiness/harness_reconcile.py --machine "$MACHINE" --apply   # APPLY: additive, backed up
python scripts/readiness/harness_reconcile.py --machine "$MACHINE"           # re-run -> expect 0 drift

# 2. WF5a #2816 / WF2 #2815 — real equality self-report (commits equality-$MACHINE.yaml)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/equality-report.ps1

# 3. WF2 #2815 — register the weekly EqualityReport task (rendered from schedule-tasks.yaml)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/setup-scheduler-tasks.ps1 -WhatIf   # preview
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/setup-scheduler-tasks.ps1           # register
powershell -NoProfile -Command "Start-ScheduledTask -TaskName 'EqualityReport' -TaskPath '\Claude\'"    # one live run

# 4. WF3 #3000 — prove the lease-arbitrated pull-dispatch claim path (DRY-RUN)
python scripts/operations/dispatch_pull.py --machine "$MACHINE"

# 5. Verify
python -c "import json,os;d=json.load(open(os.path.expanduser('~/.claude/settings.json')));print('deny entries:',len(d.get('permissions',{}).get('deny',[])))"
git log --oneline -3 -- ".claude/state/equality-$MACHINE.yaml"; ls -la ".claude/state/equality-$MACHINE.yaml"
powershell -NoProfile -Command "Get-ScheduledTask -TaskPath '\Claude\' | Format-Table TaskName,State"
git status --porcelain
```

## Notes / gotchas

- **Run as the normal user** that owns `%USERPROFILE%\.claude` so step 1 writes the right settings file.
- If step 3 errors on permissions, re-run **that step** in a Git Bash / PowerShell launched **as
  Administrator** (Task Scheduler registration can need elevation).
- **No bot token needed** — these are pull workers; only outbound `git`/`gh` auth is required (step 2
  commits + pushes `equality-$MACHINE.yaml`).
- Hostname auto-resolves (`ACMA-ANSYS05` → `ace-win-1`, `acma-ws014` → `ace-win-2`) via the registry
  `hostname_aliases`, but `--machine` is passed explicitly to avoid ambiguity.
- Step 4 is **dry-run** (no `--apply`): it proves claim → lease → release without executing real work.
  A real executor + scheduling the poll are the promotion follow-up (see the parity checklist).

## What it satisfies

| Step | Slice | Closes |
|---|---|---|
| 1 | WF1 #2999 | deny-list convergence on the Windows host (parity with a1/a2) |
| 2 | WF5a #2816 / WF2 #2815 | real `equality-<machine>.yaml` (compute no longer `unknown`); single-source parity |
| 3 | WF2 #2815 | weekly EqualityReport task registered + one validated run |
| 4 | WF3 #3000 | pull-dispatch claim path proven on a no-SSH host |

## Background

- WF3 pull model: `docs/ops/pull-dispatch-no-ssh.md`
- Parity / promotion model: `docs/ops/windows-macos-dispatch-parity.md`
- Reconciler on Windows: `.claude/skills/devops/hermes-windows-setup/` references
- Solver-license `present → licensed` (WF5b #2852) is a **separate** follow-up (needs a licensed-solver probe).
