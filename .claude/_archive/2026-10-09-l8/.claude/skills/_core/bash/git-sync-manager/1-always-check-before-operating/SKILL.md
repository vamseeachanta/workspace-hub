---
name: git-sync-manager-1-always-check-before-operating
description: 'Sub-skill of git-sync-manager: 1. Always Check Before Operating (+4).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 1. Always Check Before Operating (+4)

## 1. Always Check Before Operating

```bash
# Check for uncommitted changes before destructive operations
if ! git diff --quiet; then
    echo "Error: uncommitted changes"
    exit 1
fi
```


## 2. Use --no-verify for Batch Commits

```bash
# Skip hooks in batch operations for speed
git commit -m "message" --no-verify
```


## 3. Handle Offline/Network Errors Gracefully

```bash
# Suppress errors and provide fallback
if ! git pull --quiet 2>/dev/null; then
    echo "Warning: could not pull (offline?)"
fi
```


## 4. Track Operation Statistics

```bash
# Always maintain counters for summary
SUCCESS=0; FAILED=0; SKIPPED=0
# Update appropriately in each operation
```


## 5. Validate Git Repositories

```bash
# Always check .git directory exists
[[ -d "$repo/.git" ]] || continue
```
