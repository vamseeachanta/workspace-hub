---
name: git-advanced-common-issues
description: 'Sub-skill of git-advanced: Common Issues.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Accidental commit to wrong branch:**
```bash
# Move commit to new branch
git branch new-branch
git reset --hard HEAD~1
git checkout new-branch
```

**Undo merge:**
```bash
# If not pushed
git reset --hard HEAD~1

# If pushed
git revert -m 1 <merge-commit>
```

**Lost changes after checkout:**
```bash
# Check reflog
git reflog

# Recover from reflog
git checkout HEAD@{2}
```

**Resolve rebase conflicts:**
```bash
# During rebase conflict
git status
# Edit conflicted files
git add <resolved-files>
git rebase --continue

# Abort if needed
git rebase --abort
```

**Clean up after failed rebase:**
```bash
git rebase --abort
# Or
git reflog
git reset --hard HEAD@{n}
```
