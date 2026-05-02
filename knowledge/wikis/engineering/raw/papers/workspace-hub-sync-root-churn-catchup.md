# Archived Skill: `workspace-hub-sync-root-churn-catchup`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/workspace-hub-sync-root-churn-catchup`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/workspace-hub-sync-root-churn-catchup`
Consolidation date: 2026-04-29

---

---
name: workspace-hub-sync-root-churn-catchup
description: Catch up workspace-hub root changes that continue to appear during repo sync because live review/agent processes keep writing files after commits
version: 1.0.0
source: learned-from-use
---

# Workspace-hub sync root-churn catch-up

Use this when `./scripts/repository_sync status all` shows subrepos are clean but the workspace-hub root keeps becoming dirty again during the same session.

## When this applies
- `repository_sync status all` reports repos clean/up to date
- but root `git status` still shows new `.planning/quick/*`, `scripts/review/results/*`, plan docs, audit outputs, or `.claude/state/*`
- and there are active long-running review/agent processes such as `codex exec` or `gemini exec`

## Key insight
This is not necessarily a repo-sync failure. It is often a root-only churn problem caused by still-running processes writing new artifacts after each commit.

## Procedure
1. Run both checks separately:
   - root: `git -C /mnt/local-analysis/workspace-hub status --short --branch`
   - repos: `./scripts/repository_sync status all`
2. Inspect live processes before declaring success:
   - `ps -ef | grep -E '[c]odex exec|[g]emini exec|[c]laude'`
3. If subrepos are clean but root has new files, stage and commit the root changes:
   - `git add -A`
   - `git commit -m "chore(sync): ..."`
   - `git push origin main`
4. Immediately re-run root `git status` again.
5. If new files appeared again, repeat the catch-up loop.
6. Only claim full root cleanliness if `git status` remains clean across a short recheck window.

## Important distinctions
- `repository_sync status all` verifies managed repos; it does not guarantee the workspace-hub root will stay clean.
- A clean repo-sync result plus a dirty root means: repo sync succeeded, but root artifact churn still needs one or more catch-up commits.
- If a repo itself is still dirty, handle that repo directly before treating the situation as root-only churn.

## Common churn sources
- `.planning/quick/*.out`
- `.planning/quick/*status-comment.md`
- `scripts/review/results/*`
- plan markdown files under `docs/plans/`
- generated audit outputs
- `.claude/state/*`

## Reporting guidance
Report these separately:
1. repo-sync status across managed repos
2. workspace-hub root cleanliness status
3. whether active processes are still mutating files

This avoids falsely claiming that everything is fully clean when only the subrepos are clean.
