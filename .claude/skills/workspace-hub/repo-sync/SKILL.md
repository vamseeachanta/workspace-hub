---
name: repo-sync
description: "Smart repository synchronization across workspace-hub ecosystem — diagnoses and fixes pull failures (detached HEAD, diverged branches, uncommitted changes)"
version: 1.0.0
category: workspace-hub
last_updated: 2026-02-14
source: internal
invoke: /repo-sync
---

# Repo Sync

Smart pull-all with automatic diagnosis and repair for the workspace-hub multi-repo ecosystem.

## Usage

`/repo-sync` — Pull all repos, diagnose failures, and fix them.

Optional arguments:
- `/repo-sync pull` — Pull all repos (default)
- `/repo-sync status` — Status check only, no pulls
- `/repo-sync push` — Push all repos with unpushed commits

## What It Does

### Phase 1: Bulk Pull
Run `./scripts/repository_sync pull all` to attempt pulling every repo.

### Phase 2: Diagnose Failures
For each repo that failed, check:
1. **Detached HEAD** — submodules pinned at a commit, not on a branch
2. **Diverged branches** — local and remote have diverged, needs merge
3. **Uncommitted changes** — dirty working tree blocking pull
4. **No upstream** — no tracking branch configured

### Phase 3: Auto-Fix
Apply the appropriate fix per failure type:

| Failure | Fix |
|---------|-----|
| Detached HEAD (submodule) | `git checkout main && git pull --no-rebase` |
| Diverged branches | `git pull --no-rebase` (merge strategy) |
| Uncommitted changes | `git stash && git pull --no-rebase && git stash pop` |
| No upstream | Report only, no auto-fix |

### Phase 4: Summary
Report final status of all repos.

## Implementation

When this skill is invoked, execute these steps:

### Step 1: Run bulk pull
```bash
./scripts/repository_sync pull all
```
Capture output. Identify repos marked with `✗ Failed`.

### Step 2: For each failed repo, diagnose
```bash
cd <repo_path>
# Check if on a branch
git branch --show-current  # empty = detached HEAD

# Check for uncommitted changes
git status --porcelain

# Check divergence (only if on a branch with upstream)
git rev-list --count @{u}.. 2>/dev/null  # ahead
git rev-list --count ..@{u} 2>/dev/null  # behind
```

### Step 3: Apply fixes
Run all independent repo fixes in parallel using the Bash tool.

**Detached HEAD:**
```bash
cd <repo_path> && git checkout main && git pull --no-rebase
```

**Diverged branches:**
```bash
cd <repo_path> && git pull --no-rebase
```

**Uncommitted changes blocking pull:**
```bash
cd <repo_path> && git stash && git pull --no-rebase && git stash pop
```

If `stash pop` has conflicts, report to user — do NOT auto-resolve.

### Step 4: Report summary table
Format as markdown table:

```
| Repo | Issue | Fix Applied | Result |
|------|-------|-------------|--------|
```

## Important Notes

- **Never force-push** or `reset --hard` without explicit user approval
- **Never rebase** diverged branches — always merge (per workspace CLAUDE.md)
- **digitalmodel** and **worldenergydata** are submodules — detached HEAD is normal when workspace-hub pins a specific commit
- After fixing submodules, the workspace-hub `git status` will show them as modified (new submodule pointer) — this is expected
- If `stash pop` fails with conflicts, stop and report to user
- Use `--no-rebase` on all pulls to avoid rebase surprises on diverged repos
