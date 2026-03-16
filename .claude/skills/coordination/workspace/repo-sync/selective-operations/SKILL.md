---
name: workspace-repo-sync-selective-operations
description: 'Sub-skill of workspace-repo-sync: Selective Operations (+1).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Selective Operations (+1)

## Selective Operations


Target specific repositories:

```bash
# Multiple specific repos
./scripts/repository_sync sync digitalmodel energy -m "Update"

# Pattern-based (if supported)
./scripts/repository_sync sync "ace*" -m "Ace project updates"
```

## Parallel Execution


For faster operations on many repos:

```bash
# Built-in parallelization
./scripts/repository_sync pull all --parallel

# Or using xargs
ls -d */ | xargs -P 4 -I {} git -C {} pull
```
