---
name: workspace-repo-sync-merge-conflicts
description: 'Sub-skill of workspace-repo-sync: Merge Conflicts (+5).'
version: 1.2.0
category: coordination
type: reference
scripts_exempt: true
---

# Merge Conflicts (+5)

## Merge Conflicts


When conflicts occur:

```bash
# Status will show conflicts
./scripts/repository_sync status all

# Resolve manually in affected repo
cd affected-repo
git status
# Fix conflicts...

*See sub-skills for full details.*

## Stale Branches


Clean up old branches:

```bash
# List stale remote-tracking branches
git remote prune origin --dry-run

# Prune stale branches
git remote prune origin
```

## Recovery


If things go wrong:

```bash
# Reset to remote state
cd repo-name
git fetch origin
git reset --hard origin/main

# Or restore from backup
git reflog
git reset --hard HEAD@{2}
```

## Authentication Issues


```bash
# Verify SSH key
ssh -T git@github.com

# Check credential helper
git config --global credential.helper
```

## Network Issues


```bash
# Test connectivity
git ls-remote origin

# Use HTTPS fallback
git remote set-url origin https://github.com/user/repo.git
```

## Permission Denied


```bash
# Check file permissions
ls -la .git/

# Fix permissions
chmod -R u+rwX .git/
```
