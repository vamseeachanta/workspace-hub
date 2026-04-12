# Session Exit — Windows Claude Parity Hardening

Date: 2026-04-11
Repo: workspace-hub

## What was completed

### Packages 1–3
- Trimmed `config/agents/claude/settings.json` to a more conservative shared baseline
- Hardened active Claude hook portability for Windows/Git Bash in:
  - `.claude/hooks/skill-content-pretooluse.sh`
  - `.claude/hooks/session-governor-check.sh`
  - `.claude/hooks/cross-review-gate.sh`
- Completed session telemetry hook wiring in `.claude/settings.json`:
  - `session-logger.sh pre`
  - `session-logger.sh post`
  - `session-review.sh`

### Package 4
- Closed the repo-side Windows readiness proof-path gap:
  - `.gitignore` unignores `.claude/state/harness-readiness-licensed-win-1.yaml`
  - `scripts/readiness/harness-config.yaml` now sets `licensed-win-1.ws_hub_path: 'D:\workspace-hub'`
  - `scripts/readiness/compare-harness-state.sh` now degrades fresh non-pass Windows reports
  - `scripts/windows/setup-scheduler-tasks.ps1` documents shared readiness proof updates
  - bootstrap artifact created at `.claude/state/harness-readiness-licensed-win-1.yaml`

### Package 5
- Implemented Windows write-back parity path using the existing bridge script
- `scripts/memory/bridge-hermes-claude.sh` is now documented/structured as cross-platform
- `scripts/windows/setup-scheduler-tasks.ps1` now adds `MemoryBridgeSync` at 04:30
- `.claude/docs/new-machine-setup.md` corrected from stale "two tasks" wording to 5-task Windows Task Scheduler model
- `docs/sessions/skills-unification-stream-exit-report.md` updated so `#1918` is no longer listed as open

## Future issues created

### #2229
`feat(windows-parity): validate licensed-win-1 NightlyReadiness and MemoryBridgeSync live`

Purpose:
- replace bootstrap placeholder readiness artifact with live Windows evidence
- validate real Task Scheduler execution on `licensed-win-1`

### #2230
`chore(claude-config): formalize managed-template vs active-settings boundary`

Purpose:
- define/guard the boundary between `config/agents/claude/settings.json` and `.claude/settings.json`
- reduce future template/runtime drift

## Current working tree summary (relevant scope)

Tracked modified:
- `.claude/docs/new-machine-setup.md`
- `.gitignore`
- `config/agents/claude/settings.json`
- `docs/sessions/skills-unification-stream-exit-report.md`
- `scripts/memory/bridge-hermes-claude.sh`
- `scripts/readiness/compare-harness-state.sh`
- `scripts/readiness/harness-config.yaml`
- `scripts/windows/setup-scheduler-tasks.ps1`

Untracked:
- `.claude/state/harness-readiness-licensed-win-1.yaml`
- `docs/plans/2026-04-11-claude-windows-parity-package-4-prompt.md`
- `docs/plans/2026-04-11-claude-windows-parity-package-5-prompt.md`
- `docs/plans/2026-04-11-windows-parity-pr-description.md`

## Recommended commit grouping

1. `fix(config/agents/claude): trim shared Claude template to conservative baseline`
2. `feat(windows-parity): add tracked readiness proof and memory write-back path`
3. `docs(plans): add Windows parity execution prompts and PR draft` (optional)

## Recommended next actions

1. Commit the current scoped changes using the grouped commits above
2. Push and open/update PR using `docs/plans/2026-04-11-windows-parity-pr-description.md`
3. Execute issue #2229 on the real Windows machine to replace the bootstrap placeholder artifact
4. Execute issue #2230 to formalize the managed-template vs active-settings boundary
