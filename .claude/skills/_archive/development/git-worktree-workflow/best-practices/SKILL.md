---
name: git-worktree-workflow-best-practices
description: 'Sub-skill of git-worktree-workflow: Best Practices.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### Do


1. Use descriptive naming convention: `<project>-<purpose>`
2. Create worktrees in sibling directories (not inside project)
3. Commit or stash changes before removing worktrees
4. Prune stale worktrees regularly
5. Document active worktrees in team communication
6. Clean up merged worktrees promptly

### Don't


1. Create worktrees inside the main project directory
2. Leave uncommitted changes in worktrees before removal
3. Forget to merge/push changes from worktrees
4. Create excessive worktrees (manage actively)
5. Use worktrees for long-lived branches (use separate clones)
6. Skip the cleanup step after merging

### Naming Convention


```bash
# Pattern: <project>-<purpose>
../project-feature-auth      # Feature work
../project-hotfix-123        # Bug fix
../project-review            # Code review
../project-test              # Testing
../project-experiment        # Experiments
```

### Workspace Organization


```
/workspace/
├── project/                 # Main development
├── project-feature-a/       # Active features
├── project-feature-b/
├── project-review/          # Review worktree
└── project-archive/         # Completed features (before cleanup)
```

### Cleanup Script


```bash
#!/bin/bash
# cleanup-worktrees.sh

# Remove merged branches
git branch --merged main | grep -v main | while read branch; do
    worktree=$(git worktree list | grep "$branch" | awk '{print $1}')
    if [ -n "$worktree" ]; then
        echo "Removing worktree: $worktree"
        git worktree remove "$worktree"
    fi
done

# Prune stale references
git worktree prune
```
