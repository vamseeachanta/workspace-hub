---
name: repo-cleanup-best-practices
description: 'Sub-skill of repo-cleanup: Best Practices.'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Always verify before deleting** - Use `find` and `ls` before `rm`
2. **Use git rm for tracked files** - Preserves history and staging
3. **Update .gitignore first** - Prevents re-adding cleaned files
4. **Commit cleanup separately** - Keep cleanup commits distinct from feature work
5. **Document what was removed** - Use clear commit messages
6. **Check file sizes** - Large files may need special handling (Git LFS)
