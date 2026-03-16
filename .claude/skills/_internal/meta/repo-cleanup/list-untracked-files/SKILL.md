---
name: repo-cleanup-list-untracked-files
description: 'Sub-skill of repo-cleanup: List Untracked Files (+3).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# List Untracked Files (+3)

## List Untracked Files


```bash
# All untracked files
git status --porcelain | grep "^??"

# Untracked files with size
git status --porcelain | grep "^??" | cut -c4- | xargs -I {} sh -c 'du -h "{}" 2>/dev/null'
```

## Find Large Files


```bash
# Files larger than 1MB
find . -type f -size +1M -exec ls -lh {} \;

# Files larger than 10MB
find . -type f -size +10M -exec ls -lh {} \;

# Largest files in repo
find . -type f -exec du -h {} + 2>/dev/null | sort -rh | head -20
```

## Find Duplicates


```bash
# Find duplicate markdown files in agent directories
find . -name "*.md" -path "*/agents/*" -type f

# Find files with same name
find . -type f -name "*.py" | xargs -I {} basename {} | sort | uniq -d

# Find duplicate by content (requires md5sum)
find . -type f -exec md5sum {} + | sort | uniq -w32 -d
```

## Find Hidden Directories


```bash
# List all hidden directories
find . -maxdepth 1 -type d -name ".*" | grep -v "^\./\.git$"

# Hidden directories with sizes
du -sh .*/
```
