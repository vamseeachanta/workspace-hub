---
name: git-worktree-workflow-what-is-a-worktree
description: 'Sub-skill of git-worktree-workflow: What is a Worktree?.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# What is a Worktree?

## What is a Worktree?


```
Main repo: /project (on main branch)
Worktree 1: /project-feature-a (on feature-a branch)
Worktree 2: /project-feature-b (on feature-b branch)
Worktree 3: /project-hotfix (on hotfix branch)
```

All share the same `.git` directory but have independent working directories.
