# Stage-prompt drift enforcement — exit handoff

Date: 2026-04-10
Repo: `/mnt/local-analysis/workspace-hub`

## What was completed

The stage-prompt drift enforcement suite was implemented, tested, and pushed to `origin/main` via a clean worktree-based push.

Remote commit now on `main`:
- `b8a7f1501` — `feat(governance): add stage-prompt drift enforcement suite`

Follow-up local commit on the original working tree:
- `ff3da56af` — `test(governance): expand stage-prompt drift stub and remediation coverage`

## Pushed enforcement surfaces

- CI gate:
  - `.github/workflows/enforcement-gate.yml`
- drift analysis / remediation:
  - `scripts/analysis/stage_prompt_drift_check.py`
- local pre-push guard:
  - `scripts/enforcement/require-stage-prompt-drift.sh`
- local status/doctor command:
  - `scripts/enforcement/stage-prompt-drift-status.sh`
- compliance dashboard integration:
  - `scripts/enforcement/compliance-dashboard.sh`
- install-hooks integration:
  - `scripts/enforcement/install-hooks.sh`
- tests:
  - `tests/analysis/test_stage_prompt_drift_check.py`
  - `tests/enforcement/test_require_stage_prompt_drift.py`
  - `tests/enforcement/test_install_hooks_stage_prompt_drift.py`
  - `tests/enforcement/test_stage_prompt_drift_status.py`
  - `tests/enforcement/test_compliance_dashboard.py`
- reports:
  - `docs/reports/stage-prompt-drift-check-2026-04-10.md`
  - `docs/reports/stage-prompt-drift-check-2026-04-10.json`

## Current local state

Local `main` was reconciled with `origin/main` using a temporary merge branch, preserving local commits and local dirty state.

At handoff time:
- `main` is no longer behind `origin/main`
- local `main` is still ahead of `origin/main` by local-only commits
- local dirty state was intentionally preserved

### Important local-only commits still present on local main
These were analyzed and intentionally not pushed during the clean worktree push path:
- `906491cc0` — `chore(solver): daily dashboard regeneration`
- `a18271749` — `fix(governance): per-session tool-call counter via PPID (#2063)`
- `12a94a332` — `fix(governance): restore 200-call enforcement threshold (#2056)`
- `ff3da56af` — `test(governance): expand stage-prompt drift stub and remediation coverage`
- `f45708aea` — `chore(sync): auto-sync 2026-04-10`

## Local dirty files still preserved
These were intentionally left in place at exit:
- `.claude/skills/coordination/knowledge-source-recon/SKILL.md`
- `.claude/skills/development/git-worktree-workflow/SKILL.md`
- `.claude/skills/software-development/overnight-parallel-agent-prompts/SKILL.md`
- `.claude/skills/test-dummy-validation/dummy-backfill-test/SKILL.md`
- `.claude/state/corrections/.edit_sequence_counter`
- `.claude/state/corrections/.recent_edits`
- `.claude/state/corrections/session_20260410.jsonl`
- `.claude/state/session-signals/2026-04-10.jsonl`
- `.codex/config.toml`
- `scripts/knowledge/tests/test-knowledge-scripts.sh`
- `scripts/knowledge/wiki-ingest-cron.sh`
- plus current untracked local files such as:
  - `.claude/skills/workspace-hub/learned/`
  - `scripts/skill-extractor.py`
  - other handoff/planning artifacts present at exit time

## Local stashes preserved
Do not drop these blindly:
- `stash@{0}` or newer may shift; inspect by message first
- preserved named stashes include:
  - `reconcile-build-knowledge-index-20260410-claude`
  - `reconcile-post-merge-top-20260410-claude`
  - `reconcile-top-main-20260410-claude`
  - `hermes-temp-large-file-cleanup-2`
  - `hermes-temp-large-file-cleanup`

Recommended inspection command:
```bash
git stash list
```

## Local guard status at exit
Verified locally:
```bash
bash scripts/enforcement/stage-prompt-drift-status.sh
```
Result at exit:
- `ACTIVE`

## Compliance dashboard at exit
Verified locally:
```bash
COMPLIANCE_WINDOW_HOURS=48 bash scripts/enforcement/compliance-dashboard.sh
```
Drift event summary was visible and showed pass events from the local guard.

## Push blocker that was resolved
A prior push failed because this tracked file exceeded GitHub's 100 MB limit:
- `.claude/state/session-signals/cost-tracking.jsonl`

That file was avoided by reconstructing a clean push from a separate worktree based on `origin/main`.

## Future GitHub issues created

- `#2070` — Guard Claude state sync against oversized session-signal files
- `#2071` — Batch remediate historical stage-prompt drift with evidence summaries
- `#2073` — Expose stage-prompt drift doctor/status in CI and operator summaries

## Recommended next actions

1. Inspect and reconcile remaining local-only commits on `main` before any future push from the original worktree.
2. Review the preserved stash entries and re-apply only what is still needed.
3. Triage and execute follow-up issues:
   - `#2070` first if push hygiene remains a priority
   - `#2071` for historical drift backlog reduction
   - `#2073` for more operator/CI visibility

## Safe inspection commands for next session

```bash
git status --short
git rev-list --left-right --count origin/main...HEAD
git log --oneline --decorate --graph -n 20
git stash list
bash scripts/enforcement/stage-prompt-drift-status.sh
COMPLIANCE_WINDOW_HOURS=48 bash scripts/enforcement/compliance-dashboard.sh
```
