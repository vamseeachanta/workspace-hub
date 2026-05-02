# Archived Skill: `workspace-hub-sync-concurrent-writer-blocks`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/workspace-hub-sync-concurrent-writer-blocks`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/workspace-hub-sync-concurrent-writer-blocks`
Consolidation date: 2026-04-29

---

---
name: workspace-hub-sync-concurrent-writer-blocks
description: Handle repository_sync cleanup when workspace-hub root is being mutated by concurrent Claude/Codex/Gemini sessions.
version: 1.0.0
source: session-learned
---

# Workspace-hub sync blocked by concurrent writers

Use this when multi-repo sync is mostly done but `workspace-hub` root will not stay clean because other active AI sessions are still writing files, creating locks, or stashing changes.

## Symptoms
- `./scripts/repository_sync status all` shows subrepos clean, but root `git status` keeps changing between checks.
- `.git/index.lock` appears intermittently.
- `ps -ef | grep '[g]it'` shows active `git status`, `git stash`, `git add`, or commit processes from other sessions.
- Strange transient untracked files appear, especially partial markdown-heading fragments like:
  - `**Complexity:**`
  - `**Date:**`
  - `**Issue:**`
  - `**Review`
  - `Compatibility`
  - `This`
  These are a strong signal that another session is mid-write and the filesystem state is not stable.

## Safe procedure
1. Run `./scripts/repository_sync status all` from workspace-hub and separate subrepo health from root health.
2. If listed repos are clean/up to date, treat subrepo sync as complete even if workspace-hub root is still dirty.
3. Inspect concurrent activity before retrying root cleanup:
   - `git status --short --branch`
   - `ps -ef | grep '[g]it'`
   - optionally `stat .git/index.lock` if a lock exists
4. If active git/session writers are still present, stop chasing a final clean root claim.
5. Report explicitly:
   - subrepos are synced/clean
   - workspace-hub root cleanup is blocked by concurrent writers
   - a final catch-up commit should happen only after those sessions finish
6. Only after active writers stop, do one final root cleanup pass:
   - `git status --short --branch`
   - `git add -A`
   - `git commit -m "chore(sync): ..."`
   - `git push origin main`
   - rerun `./scripts/repository_sync status all`

## Do not
- Do not claim workspace-hub root is finally clean while active sessions are still writing.
- Do not repeatedly remove `index.lock` without checking for live git processes.
- Do not treat weird transient filenames as normal repo files to preserve without first confirming they are intentional.

## Outcome pattern
The correct end-state may be:
- repo ecosystem sync: complete
- workspace-hub root: temporarily blocked by concurrent writers

That is better than a false claim of full cleanliness.
