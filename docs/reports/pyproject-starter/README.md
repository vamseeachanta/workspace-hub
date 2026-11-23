# pyproject-starter archived sync exception

Date: 2026-04-13
Repo under inspection: `pyproject-starter`

## Current state
- Remote URL from workspace config: `https://github.com/vamseeachanta/pyproject-starter.git`
- Remote is archived/read-only, so normal ecosystem push cannot succeed.
- Branch: `master`
- Local HEAD: `cd6eae9`
- Upstream HEAD: `6d55266`
- Ahead by 1 commit

## Ahead commit
- `cd6eae9` — `chore(sync): auto-sync 2026-02-23`

## Classification
Preliminary classification: `needs-review-before-preserve`

Reason:
- This is not a small metadata drift commit.
- Diffstat shows a large destructive change:
  - 137 files changed
  - 2 insertions
  - 37,493 deletions
- The commit appears to remove major portions of Agent OS / command / docs structure.
- It should not be migrated blindly into any successor repo.

## Exported artifact
- Patch file: `docs/reports/pyproject-starter/cd6eae9-auto-sync-2026-02-23.patch`
- Patch size: about 1.35 MB

## Successor-repo reconnaissance
No clear writable successor repo was identified automatically from the workspace portfolio scan.

Signals found:
- `docs/standards/FILE_STRUCTURE_TAXONOMY.md` suggests `pyproject-starter/` may be better treated as a template path and possibly moved to `templates/pyproject-starter/` or removed if unused.
- Workspace skills reference `python-project-template`, but that is a skill/workflow concept, not an identified git successor for this repository.
- Therefore the safe default is: preserve the patch artifact and require explicit human/repo-owner decision before migration.

## Recommended next step
1. Review commit `cd6eae9` manually.
2. Decide one of:
   - abandon and document,
   - preserve as archive-only,
   - selectively port pieces to a new writable template repo/path.
3. Track that decision in GitHub issue `#2259`.
