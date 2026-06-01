# Session Handoff — Harness-update native rollout + repo-housekeeping tooling

**Date:** 2026-05-31
**Host:** ace-linux-2 (dev-secondary)
**Scope:** Make AI-harness CLI updates work fleet-wide via native updaters; build a safe ecosystem-wide git-housekeeping script.
**Tracking issue:** [#2920](https://github.com/vamseeachanta/workspace-hub/issues/2920)

---

## Outcome (all verified)

### 1. Native harness updater is canonical and LIVE on both Linux boxes
Decision **A** on [#2920](https://github.com/vamseeachanta/workspace-hub/issues/2920): the canonical updater is the **native** `scripts/maintenance/update-harness-tools.sh`
(`hermes update` / `claude update` / `codex update` / gemini via npm), **not** the older npm-based
`scripts/cron/harness-update.sh` (retained in-repo, no longer scheduled). Missing tools are skipped per machine.

| Machine | Schedule | State | Evidence |
|---|---|---|---|
| ace-linux-2 | cron `45 1 * * *` | ✅ live | literal crontab cmd run under `env -i` → exit 0, 4/4 ok, dated log written |
| ace-linux-1 | cron `15 1 * * *` | ✅ live | same end-to-end test → exit 0, 4/4 ok; old npm cron line removed (backup in `/tmp/crontab.bak.*`) |
| licensed-win-1/2 | Task Scheduler `02:15` | ⏳ ready, NOT installed | needs admin `setup-scheduler-tasks.ps1` run (no SSH) |
| macbook-portable | — | manual | `schedule_variant: none` |

Tools updated on both Linux boxes during the session (gemini **0.38.2 → 0.44.1**; hermes/claude/codex already current).

### 2. `scripts/maintenance/repo-housekeeping.sh` — new safe multi-repo git housekeeping
Dry-run-default sweep over sibling repos: commit WIP (incl. linked worktrees), push topic branches, open PRs to main
(**never** auto-merges/pushes main — PR-for-everything), prune merged branches/worktrees/dirs.
Guards: archival/backup branch names + `--max-ahead` skip junk PRs; merge detection vs **origin/main** via `git cherry`
(catches squash/rebase merges); secret-file denylist; `--no-clean-dirs` to skip untracked-dir removal; per-repo error isolation.

### 3. workspace-hub branch hygiene done
Pruned 4 merged branches + 1 stale linked worktree (`workspace-hub-2817-plan-approval-gate`) + dangling `worktrees/issue-2464` pointer.

---

## PRs (all MERGED)
- [#2922](https://github.com/vamseeachanta/workspace-hub/pull/2922) — native updater canonical (schedule-tasks.yaml + bootstrap §2.9 symlink)
- [#2923](https://github.com/vamseeachanta/workspace-hub/pull/2923) — add repo-housekeeping.sh
- [#2927](https://github.com/vamseeachanta/workspace-hub/pull/2927) — Windows Task Scheduler support (+ PATH hardening for cron/Task-Scheduler minimal env)
- [#2928](https://github.com/vamseeachanta/workspace-hub/pull/2928) — housekeeping: detect merges vs origin/main (fix duplicate PRs)
- [#2929](https://github.com/vamseeachanta/workspace-hub/pull/2929) — housekeeping: `--no-clean-dirs` flag

## Repo state at exit
- **workspace-hub** `main`: behind origin by 1 (the #2929 merge — `git pull` to sync). Working tree carries **other agents'** uncommitted work (deckhand #2900 plans, `hermes-ecosystem-integration/SKILL.md`, session-signals/ai-tools-status cron churn) — **left untouched** per multi-agent serialization. Not from this session.
- Local branches kept intentionally: `backup/pre-rebase-20260413-152018` (archival), `codex/ace-linux-2-20260427-issue-2464` (1 commit, 5 wk, unmerged). `docs/untracked-artifacts-2026-05-31` belongs to another session.
- **ace-linux-1**: cron + `~/.local/bin/update-harness-tools` symlink installed; no repo commits made there (script placed via targeted `git checkout origin/main -- <file>`, no full pull on the dirty dev-primary).

## No external action pending from automation
No emails, no external posts. All GitHub writes were the 5 PRs above + comments on [#2920](https://github.com/vamseeachanta/workspace-hub/issues/2920)/#2919.

## Next steps (USER)
1. **Windows**: on licensed-win-1 and -2, Administrator PowerShell → `cd D:\workspace-hub; git pull; powershell -ExecutionPolicy Bypass -File scripts\windows\setup-scheduler-tasks.ps1 -WhatIf` (also the PS-syntax check), then without `-WhatIf` to install; `Start-ScheduledTask -TaskName 'HarnessUpdate' -TaskPath '\Claude\'` to smoke-test.
2. **Decide** on the two leftover workspace-hub branches (`codex/ace-linux-2-...`, `backup/pre-rebase-...`) — keep or delete.
3. **First broad `repo-housekeeping --apply`** across the other 12 repos is parked: their only ahead-branches are 10–11 month abandoned archives (correctly skipped by guards), so no urgency. When ready, start conservative: `repo-housekeeping.sh --no-pr --no-clean-dirs --apply`.

## Notes for next session
- Registry stale field: `config/workstations/registry.yaml` lists ace-linux-1 `agent_clis: [claude, gemini]` but **codex AND claude are actually installed** there.
- workspace-hub has a post-merge hook (kanban-autoload) that can hang a `git pull` past its timeout; the fast-forward itself completes — verify with `git rev-list --left-right --count HEAD...origin/main`.
- Memory written: `harness-update-native-canonical` (per-machine state).
