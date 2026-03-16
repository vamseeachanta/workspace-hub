---
name: workspace-repo-sync-daily-development-workflow
description: 'Sub-skill of workspace-repo-sync: Daily Development Workflow (+2).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Daily Development Workflow (+2)

## Daily Development Workflow


```bash
# Morning: Pull latest
./scripts/repository_sync pull all

# During day: Work on code...

# End of day: Sync everything
./scripts/repository_sync sync all -m "$(date +%Y-%m-%d) updates"
```

## Feature Branch Workflow


```bash
# Start feature in all work repos
./scripts/repository_sync switch work feature/new-feature

# Develop across repos...

# Keep in sync with main
./scripts/repository_sync sync-main work

# Push feature branches
./scripts/repository_sync push work

# Return to main
./scripts/repository_sync switch work main
```

## Release Workflow


```bash
# Create release branch
./scripts/repository_sync switch work release/v1.2.0

# Final sync and push
./scripts/repository_sync sync work -m "Release v1.2.0 preparation"

# After merge, back to main
./scripts/repository_sync switch work main
./scripts/repository_sync pull work
```
