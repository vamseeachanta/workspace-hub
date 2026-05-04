---
name: git-advanced-1-commit-history
description: 'Sub-skill of git-advanced: 1. Commit History (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Commit History (+2)

## 1. Commit History


```bash
# Write good commit messages
git commit -m "feat(auth): add OAuth2 support

- Add Google OAuth provider
- Implement token refresh logic
- Add user profile sync

Closes #123"

# Keep commits atomic
# One logical change per commit

# Use conventional commits
# feat: new feature
# fix: bug fix
# docs: documentation
# style: formatting
# refactor: code restructure
# test: add tests
# chore: maintenance
```


## 2. Branch Strategy


```bash
# Feature branches from main
git checkout -b feature/add-auth main

# Hotfix branches from main
git checkout -b hotfix/fix-login main

# Keep branches short-lived
# Merge frequently

# Delete merged branches
git branch -d feature/add-auth
```


## 3. Rebase vs Merge


```bash
# Use rebase for:
# - Cleaning up local commits
# - Updating feature branch from main
git rebase main

# Use merge for:
# - Integrating feature into main
# - Preserving branch history
git merge --no-ff feature/add-auth
```
