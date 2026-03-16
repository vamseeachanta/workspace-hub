---
name: sync-error-handling
description: 'Sub-skill of sync: Error Handling.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Error Handling

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
