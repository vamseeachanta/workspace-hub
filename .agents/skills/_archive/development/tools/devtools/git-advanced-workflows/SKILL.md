---
name: devtools-git-advanced-workflows
description: 'Sub-skill of devtools: Git Advanced Workflows (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Git Advanced Workflows (+1)

## Git Advanced Workflows

```bash
# See git-advanced for complete patterns

# Git worktrees - work on multiple branches simultaneously
git worktree add ../feature-branch feature/new-feature
git worktree add ../hotfix-branch hotfix/urgent-fix
git worktree list
git worktree remove ../feature-branch

# Git bisect - find the commit that introduced a bug
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git will checkout commits for you to test
git bisect run ./test.sh  # Automate with a script
git bisect reset

# Git reflog - recover lost commits
git reflog
git checkout HEAD@{5}  # Go back to a previous state
git branch recovered-branch HEAD@{5}  # Create branch from lost commit

# Git rerere - reuse recorded resolution
git config rerere.enabled true
# Now git remembers how you resolved conflicts

# Interactive rebase patterns
git rebase -i HEAD~5
# Commands in editor:
#   pick   - use commit
#   reword - edit commit message
#   edit   - stop and amend
#   squash - combine with previous
#   fixup  - combine, discard message
#   drop   - remove commit

# Git hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run tests before commit
npm test || exit 1

# Run linter
npm run lint || exit 1
EOF
chmod +x .git/hooks/pre-commit

# Shared hooks with husky
npx husky init
echo "npm test" > .husky/pre-commit
```


## Raycast/Alfred Automation

```bash
# See raycast-alfred for complete patterns

# Raycast script command (bash)
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open Project
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 📁
# @raycast.argument1 { "type": "text", "placeholder": "project name" }

PROJECT="$1"
PROJECT_DIR="$HOME/projects/$PROJECT"

if [ -d "$PROJECT_DIR" ]; then
    code "$PROJECT_DIR"
    echo "Opened $PROJECT"
else
    echo "Project not found: $PROJECT"
fi
```
