---
name: workspace-repo-sync-list-branches
description: 'Sub-skill of workspace-repo-sync: List Branches (+3).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# List Branches (+3)

## List Branches


```bash
# Show branches in all repos
./scripts/repository_sync branches all

# Show branches in work repos
./scripts/repository_sync branches work
```

## Fetch Remote Branches


Track all remote branches locally:

```bash
./scripts/repository_sync fetch-branches all
```

## Sync with Main


Update feature branches with main:

```bash
# Merge main into current branches
./scripts/repository_sync sync-main all

# Rebase instead of merge
./scripts/repository_sync sync-main all --rebase
```

## Switch Branches


Switch all repos to a specific branch:

```bash
# Switch to main
./scripts/repository_sync switch all main

# Switch to feature branch
./scripts/repository_sync switch work feature/new-design
```
