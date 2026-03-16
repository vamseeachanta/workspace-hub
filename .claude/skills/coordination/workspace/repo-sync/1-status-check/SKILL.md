---
name: workspace-repo-sync-1-status-check
description: 'Sub-skill of workspace-repo-sync: 1. Status Check (+4).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Status Check (+4)

## 1. Status Check


View the state of all repositories:

```bash
./scripts/repository_sync status all
```

**Output indicators:**
- 🟢 **Clean**: No changes, up to date
- 🔴 **Uncommitted**: Has local changes
- 🟣 **Unpushed**: Has commits not pushed
- 🔵 **Behind**: Remote has updates
- 🟡 **Not cloned**: Repository missing locally

## 2. Pull Operations


Fetch and merge from remote:

```bash
# Pull all repositories
./scripts/repository_sync pull all

# Pull only work repos
./scripts/repository_sync pull work

# Pull specific repo
./scripts/repository_sync pull digitalmodel
```

## 3. Commit Operations


Stage and commit changes:

```bash
# Commit all with default message
./scripts/repository_sync commit all

# Commit with custom message
./scripts/repository_sync commit all -m "Update dependencies"

# Commit work repos only
./scripts/repository_sync commit work -m "Weekly sync"
```

## 4. Push Operations


Push committed changes to remote:

```bash
# Push all repositories
./scripts/repository_sync push all

# Push work repos
./scripts/repository_sync push work
```

## 5. Full Sync (Commit + Push)


Complete synchronization in one command:

```bash
# Sync all repos
./scripts/repository_sync sync all -m "End of day sync"

# Sync work repos
./scripts/repository_sync sync work -m "Client updates"
```
