---
name: git-worktree-workflow-github-actions-parallel-jobs
description: 'Sub-skill of git-worktree-workflow: GitHub Actions Parallel Jobs.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# GitHub Actions Parallel Jobs

## GitHub Actions Parallel Jobs


```yaml
jobs:
  parallel-claude:
    strategy:
      matrix:
        task: [lint, test, security]
    steps:
      - uses: actions/checkout@v4

      - name: Create worktree

*See sub-skills for full details.*
