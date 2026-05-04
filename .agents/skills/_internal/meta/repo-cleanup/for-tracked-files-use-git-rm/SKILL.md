---
name: repo-cleanup-for-tracked-files-use-git-rm
description: 'Sub-skill of repo-cleanup: For Tracked Files (Use git rm) (+2).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# For Tracked Files (Use git rm) (+2)

## For Tracked Files (Use git rm)


```bash
# Remove tracked file
git rm path/to/file

# Remove tracked directory
git rm -r path/to/directory

# Remove from git but keep local copy
git rm --cached path/to/file
```

## For Untracked Files (Use rm)


```bash
# Remove untracked file
rm path/to/file

# Remove untracked directory
rm -rf path/to/directory

# Interactive removal (safer)
rm -i path/to/file
```

## Dry Run First


```bash
# Preview what would be deleted
git clean -n -d

# Preview including ignored files
git clean -n -d -x
```
