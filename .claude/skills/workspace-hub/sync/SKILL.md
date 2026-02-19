---
name: sync
version: "1.0.0"
category: workspace-hub
description: "Fast verified multi-repo synchronization across workspace-hub submodules"
capabilities: []
requires: []
see_also: []
---
# /sync — Workspace Hub Repository Synchronization

Fast, verified multi-repo synchronization across all workspace-hub submodules.

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

# Detect detached HEAD
if ! git symbolic-ref -q HEAD > /dev/null 2>&1; then
    echo "DETACHED: $repo"
    git checkout main 2>/dev/null || git checkout master
fi

# Detect uncommitted changes
if ! git diff --quiet HEAD 2>/dev/null; then
    echo "DIRTY: $repo"
fi

# Detect divergence
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
```

### Phase 3: Pull (with stash safety)

```bash
cd "$WORKSPACE_ROOT/$repo"

# Stash if dirty
if ! git diff --quiet HEAD 2>/dev/null; then
    git stash push -m "pre-sync-$(date +%Y%m%d-%H%M%S)"
    STASHED=true
fi

# Pull with rebase (never merge for sync pulls)
git pull --rebase origin main

# Pop stash if we stashed
if [ "$STASHED" = true ]; then
    git stash pop || echo "STASH CONFLICT in $repo — report to user, do NOT auto-resolve"
fi
```

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
- [ ] No stash pop conflicts (if any stashes were used)

Present a status table:

```
| Repository          | Branch | Status  | Behind | Ahead |
|---------------------|--------|---------|--------|-------|
| assetutilities      | main   | clean   | 0      | 0     |
| rock-oil-field      | main   | clean   | 0      | 0     |
| digitalmodel        | main   | clean   | 0      | 0     |
| ...                 | ...    | ...     | ...    | ...   |
```

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

## Error Handling

### Detached HEAD
```bash
cd "$WORKSPACE_ROOT/$repo"
git checkout main 2>/dev/null || git checkout master
git pull --rebase origin main
```

### Diverged History (force-pushed remote)
```bash
# Detect: behind > 0 AND ahead > 0
# DO NOT auto-resolve — ask user:
echo "$repo has diverged: $BEHIND behind, $AHEAD ahead"
echo "Options: merge, reset --hard origin/main, or skip"
```

### Stash Pop Conflict
```bash
# Report to user, do NOT auto-resolve
echo "Stash pop conflict in $repo — manual resolution required"
git stash list
```

### CRLF / Line Ending Issues
```bash
# Fix shell scripts to LF
git config core.autocrlf input
# Or per-file: dos2unix script.sh
```

## Windows / MINGW64 Notes

- Path root is `/d/workspace-hub/` (not `D:\`)
- `while [ "$(pwd)" != / ]` loops never terminate — use `$WORKSPACE_ROOT` var
- `mklink /J` for junctions requires unquoted paths
- Shell scripts must use LF endings (CRLF breaks bash)
- Enable long paths: `git config --global core.longpaths true`

## Anti-Patterns (NEVER do these)

- NEVER parse `.gitignore` to discover repos — use `.gitmodules`
- NEVER report sync as successful without verification phase
- NEVER auto-resolve stash pop conflicts or merge conflicts
- NEVER force-push without explicit user confirmation
- NEVER skip repos silently — report every repo's status
- NEVER use `git add -A` without first running `git status`
