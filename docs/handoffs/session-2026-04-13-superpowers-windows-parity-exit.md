# Session Exit — Superpowers sync fix + Windows parity follow-ups

Date: 2026-04-13
Repo: workspace-hub

## What was completed

### 1. Superpowers harness updater fixed
- Root cause identified:
  - `harness-update.sh` was attempting `claude plugin update superpowers`
  - actual installed plugin id is `superpowers@claude-plugins-official`
  - plugin is project-scoped, not user-scoped on this machine
- `scripts/cron/harness-update.sh` was updated to:
  - query `claude plugin list --json`
  - detect installed Superpowers scope(s)
  - use the full installed plugin id for update calls
  - report healthy `up-to-date` state when already current

### 2. Regression coverage added
- Added and extended:
  - `tests/work-queue/test-harness-update-superpowers.sh`
- Current checks assert:
  - JSON plugin inventory is used
  - scope-aware update path exists
  - Superpowers health is based on installed inventory
  - updater uses full installed plugin id

### 3. Live verification completed on ace-linux-1
- Regression test passes (`4/4`)
- `bash scripts/cron/harness-update.sh --dry-run` reports:
  - `Superpowers: [dry-run] scopes=project:5.0.7:true`
- Real run reports:
  - `Superpowers: updating scope=project version=5.0.7 enabled=true id=superpowers@claude-plugins-official`
  - plugin already at latest
  - summary status `up-to-date`, health `healthy`

### 4. Repo ecosystem skill sync verified
- Ran Hermes skills backfill
- Current result:
  - `No drift — all skills in sync across 6 repos`

### 5. Licensed Windows machine direct-verification task prepared
- Updated existing issue:
  - `#2229 feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live`
- Added a direct-on-machine verification checklist comment covering:
  - repo pull
  - scheduler re-registration
  - RepoSync cadence check
  - Superpowers regression test + dry-run verification
  - NightlyReadiness artifact replacement
  - MemoryBridgeSync verification
- Added label:
  - `status:plan-review`

## Commits pushed
- `7134e2e0d` — `fix(harness): update superpowers via installed plugin id`
- `6bf8480b4` — `test(harness): assert superpowers updater uses plugin id`

## Future GitHub issues created

### #2257
`fix(windows-scheduler): align RepoSync cadence with schedule-tasks source of truth`

Why:
- `config/scheduled-tasks/schedule-tasks.yaml` says Windows RepoSync is every 4 hours
- `scripts/windows/setup-scheduler-tasks.ps1` still registers RepoSync daily at `11:30PM`

### #2258
`feat(parity): track Claude plugin inventory in ai-tools-status reports`

Why:
- current parity reports track CLI binaries but not installed Claude plugins/scopes
- project-scoped plugin drift like Superpowers was therefore invisible in normal parity reporting

## Verified current state
- Superpowers updater fix is on `main` and `origin/main`
- Windows consumption path exists via repo sync:
  - `scripts/windows/repo-sync-daily.sh`
  - `scripts/windows/setup-scheduler-tasks.ps1`
  - `config/workstations/registry.yaml` points Windows workstations at `D:\workspace-hub`
- Remaining caveat:
  - `licensed-win-1` is still marked unreachable in `config/ai_agents/ai-tools-status.yaml`, so live Windows execution remains unverified from this Linux session

## Recommended next actions
1. Execute issue `#2229` directly on `licensed-win-1`
2. Fix Windows RepoSync scheduler cadence via `#2257`
3. Extend parity reporting to include Claude plugins via `#2258`
4. After direct Windows verification, replace placeholder readiness evidence with live committed artifact
