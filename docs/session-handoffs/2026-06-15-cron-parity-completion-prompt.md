# Handoff prompt — finish cron parity (Windows + allowlist re-land)

**Context (2026-06-15):** Linux crontab parity is DONE. `ace-linux-1` (dev-primary)
generates the daily readiness/ecosystem reports (cataloged=47, uncataloged=0);
`ace-linux-2` (dev-secondary) consumes them and now runs its 9 canonical tasks with
the previously-dead `$WORKSPACE_HUB` managed block restored to absolute paths plus the
`equivalence`/`parity` sentinels. The session-analysis gap (06-08…06-12) was backfilled.
Three items remain.

## 1. Windows boxes — `ace-win-1`, `ace-win-2` (contribute-minimal role)
On each box, in an **Administrator** PowerShell:

```powershell
cd D:\workspace-hub
git pull --rebase --autostash
powershell -ExecutionPolicy Bypass -File scripts\windows\setup-scheduler-tasks.ps1 -WhatIf   # preview
powershell -ExecutionPolicy Bypass -File scripts\windows\setup-scheduler-tasks.ps1            # apply
Get-ScheduledTask -TaskPath "\Claude\" | Format-Table TaskName,State                          # verify
```

Idempotent; auto-detects host (`ace-win-1`/`acma-ansys05*`, `ace-win-2`/`acma-ws014*`);
`WorkspaceRoot` auto-resolves; Git Bash at `C:\Program Files\Git\bin\bash.exe`. `-Remove` to undo.
Prereqs: repo at `D:\workspace-hub`, `gh` authed, Tailscale up. Confirm the boxes are online first
(they were unreachable from ace-linux-2 — no Tailscale Windows peers).

## 2. Re-land the cron allowlist (sanitized)
Add 4 fingerprints to `config/workstations/harness-state-classes.yaml` **from a dedicated
checkout** (see warning below): deckhand `sweep-deliverables.py`, `patch-guard.py`,
`hermes-update-sentinel.py` (each `cwd_contains` + `script_basename`), and one external
weekday job — `owner: external-private-repo`, `command_contains: market-alerts/cron.sh`
(path-only, **no owning-repo name** per PII epic #3095). Verify:
`uv run --no-project python scripts/cron/cron-audit.py` → `uncataloged=0`.

## 3. Clean up the aborted push
Delete the errant remote branch `epic-3095/3098-phase3-functional-files` — it holds a
non-sanitized external-repo entry from a push that collided with a concurrent session.

## ⚠️ Hazard
`/mnt/local-analysis/workspace-hub` is a SHARED clone whose HEAD switches branches mid-session
(bot/PII-epic work). Never `git commit`/`push` non-bot changes there — use a separate
`git worktree` off `origin/main`. The installed crontabs are independent of git and already live.
