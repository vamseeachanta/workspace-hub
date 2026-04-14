---
name: sync
version: 1.0.0
category: workspace
description: Fast, verified multi-repo synchronization across all workspace-hub submodules
  including pull, push, and submodule pointer updates.
type: reference
tags: []
---

# Sync

## Usage

```
/sync [subcommand] [scope]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| (default) | Full sync: pull all → commit dirty → push → update pointers → verify |
| `status` | Show status table for all repos (clean/dirty/unpushed/behind) |
| `pull` | Pull latest from all repos (stash uncommitted first) |
| `push` | Push all repos with unpushed commits |
| `pointers` | Update workspace-hub submodule pointers and push |

## Scope

- `all` (default) — All 26 submodules
- `work` — Work repositories only
- `personal` — Personal repositories only
- `<repo-name>` — Single specific repository

## Execution Protocol

**CRITICAL**: This skill exists because git sync is the #1 activity (68+ sessions) and the #1 source of friction. Follow this protocol exactly.
### Phase 1: Discovery (read .gitmodules, NOT .gitignore)

```bash
WORKSPACE_ROOT="/d/workspace-hub"
cd "$WORKSPACE_ROOT"

# Get submodule list from .gitmodules (NEVER parse .gitignore)
git submodule status
```
### Phase 2: Pre-flight checks

For each submodule:
1. Check if HEAD is detached → fix to tracking branch
2. Check for uncommitted changes → stash before pull
3. Check for divergence: `git rev-list --count HEAD..origin/main` and `git rev-list --count origin/main..HEAD`

```bash
# Per-repo status check
cd "$WORKSPACE_ROOT/$repo"
git fetch origin --quiet


*See sub-skills for full details.*
### Phase 3: Pull (with stash safety)

```bash
cd "$WORKSPACE_ROOT/$repo"

# Stash if dirty
if ! git diff --quiet HEAD 2>/dev/null; then
    git stash push -m "pre-sync-$(date +%Y%m%d-%H%M%S)"
    STASHED=true
fi

# Pull with rebase (never merge for sync pulls)

*See sub-skills for full details.*
### Phase 4: Commit dirty repos

```bash
cd "$WORKSPACE_ROOT/$repo"
if ! git diff --quiet HEAD 2>/dev/null; then
    git add -A
    git commit -m "chore: sync updates

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
fi
```
### Phase 5: Push

```bash
cd "$WORKSPACE_ROOT/$repo"
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
if [ "$AHEAD" -gt 0 ]; then
    git push origin main
fi
```
### Phase 6: Update workspace-hub submodule pointers

```bash
cd "$WORKSPACE_ROOT"
git add $(git submodule status | awk '{print $2}')
if ! git diff --cached --quiet; then
    git commit -m "chore: sync submodule pointers

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
    git push origin main
fi
```
### Phase 7: Verification (MANDATORY — never skip)

```bash
cd "$WORKSPACE_ROOT"
git submodule status
```

**Success criteria** (ALL must pass before reporting success):
- [ ] No submodules in detached HEAD state
- [ ] No submodules with uncommitted changes
- [ ] No submodules with unpushed commits
- [ ] Workspace-hub submodule pointers match remote HEAD

*See sub-skills for full details.*

## Existing Script

The `./scripts/repository_sync` script handles the mechanics:

```bash
# Quick status of all repos
./scripts/repository_sync status all

# Pull all
./scripts/repository_sync pull all

# Full sync (commit + push)
./scripts/repository_sync sync all -m "End of day sync"
```

Use the script where it works. Fall back to manual git commands per-repo when the script doesn't cover a case (detached HEAD fix, stash conflict resolution, submodule pointer updates).

## Windows / MINGW64 Notes

- Path root is `/d/workspace-hub/` (not `D:\`)
- `while [ "$(pwd)" != / ]` loops never terminate — use `$WORKSPACE_ROOT` var
- `mklink /J` for junctions requires unquoted paths
- Shell scripts must use LF endings (CRLF breaks bash)
- Enable long paths: `git config --global core.longpaths true`

## Git LFS Push Failure Triage

If a repo push fails only because a Git LFS pre-push hook is installed but `git-lfs` is missing on the machine:

1. Check whether the outgoing commit actually includes any files tracked by LFS patterns from `.gitattributes`.
2. If the commit only changes normal text/code/docs files and does not add or modify any LFS-tracked files, a safe fallback is:

```bash
git push --no-verify origin main
```

3. Record that `git-lfs` is missing and recommend proper installation for future binary/LFS pushes.

Do **not** use `--no-verify` if the commit includes files that match LFS patterns such as `*.zip`, `*.pdf`, `*.pptx`, or any other configured LFS paths.

## Stale Gitlink / Missing `.gitmodules` Triage

If root verification fails with:

```text
fatal: no submodule mapping found in .gitmodules for path '<path>'
```

then the repo likely contains a stale gitlink entry (mode `160000`) for a path that is no longer declared in `.gitmodules`.

Diagnosis:

```bash
git ls-files --stage <path>
git ls-tree HEAD <path>
git show HEAD:.gitmodules
```

If `HEAD`/index still show the path as a gitlink but `.gitmodules` is missing or has no matching entry, and the directory on disk is just an empty leftover, a safe cleanup is:

```bash
git rm --cached <path>
rmdir <path> 2>/dev/null || true
git commit -m "fix(git): remove stale <path> gitlink"
```

Then rerun:

```bash
git submodule status
git status --short
```

Do not remove the gitlink blindly if the path still has a valid `.gitmodules` entry or contains real local work that has not been reviewed.

## Anti-Patterns (NEVER do these)

- NEVER parse `.gitignore` to discover repos — use `.gitmodules`
- NEVER report sync as successful without verification phase
- NEVER auto-resolve stash pop conflicts or merge conflicts
- NEVER bypass Git LFS hooks with `--no-verify` before confirming the pushed commit contains no LFS-tracked files
- NEVER force-push without explicit user confirmation
- NEVER skip repos silently — report every repo's status
- NEVER use `git add -A` without first running `git status`

## Iron Law

> No sync shall be reported as successful without completing Phase 7 verification and confirming all four success criteria pass — ever.

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "All the pushes succeeded so it's done" | Push success does not equal sync success. Detached HEADs, dirty repos, and pointer mismatches are invisible without verification. |
| "Verification is redundant — I watched each step succeed" | Individual step success does not guarantee end-state correctness. Verification checks the final state, not the steps. |
| "I'll skip verification because the user is waiting" | A false-positive "sync complete" causes harder-to-debug failures later. The 10 seconds verification takes prevents hours of debugging. |
| "Only one repo changed, no need for full verification" | Submodule pointers and cross-repo state can break from a single repo change. Always verify all four criteria. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "sync looks good" (without running `git submodule status`)
- "all repos pulled successfully, we're done"
- "skipping verification to save time"
- "probably fine — no errors were reported"

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
