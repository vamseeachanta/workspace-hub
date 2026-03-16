---
name: workspace-repo-sync-commit-messages
description: 'Sub-skill of workspace-repo-sync: Commit Messages (+2).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Commit Messages (+2)

## Commit Messages


Use consistent format:

```
[scope] action: description

Examples:
[all] update: Dependency refresh
[work] fix: Security patches
[docs] add: API documentation
```


## Frequency


- **Pull**: Start of each work session
- **Commit**: After completing logical units
- **Push**: End of work session or before breaks
- **Sync**: Daily minimum


## Verification


Always verify before pushing:

```bash
# Check what will be pushed
./scripts/repository_sync status all

# Review specific repo changes
cd repo-name && git diff origin/main
```
