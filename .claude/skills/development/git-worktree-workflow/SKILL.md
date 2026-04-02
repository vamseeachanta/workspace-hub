---
name: git-worktree-workflow
description: Use git worktrees for parallel Claude Code workflows. Run multiple Claude
  instances on different features simultaneously without merge conflicts. Use for
  parallel development, multi-branch testing, and subagent workflows.
type: reference
version: 1.1.0
last_updated: 2026-01-02
category: development
related_skills:
- repo-sync
- git-worktree-workflow
capabilities: []
requires: []
tags: []
---

# Git Worktree Workflow

## Overview

Git worktrees allow you to have multiple working directories from a single repository, enabling parallel development workflows with Claude Code. This is essential for running multiple Claude instances on different tasks simultaneously.

## Quick Start

```bash
# 1. Create worktree for new feature branch
git worktree add -b feature-api ../project-api main

# 2. Run Claude in worktree
cd ../project-api && claude "Implement the feature"

# 3. After completion, merge and cleanup
cd ../project
git merge feature-api
git worktree remove ../project-api
git branch -d feature-api
```

## When to Use

- Running multiple Claude agents on different features
- Testing changes while continuing development
- Code review with live comparison
- Parallel bug fixes across branches
- Subagent verification workflows
- A/B implementation comparisons
- CI/CD parallel job execution

## Related Skills

- [repo-sync](../repo-sync/SKILL.md) - Manage multiple repositories
- [sparc-workflow](../sparc-workflow/SKILL.md) - Systematic development process
- [agent-orchestration](../agent-orchestration/SKILL.md) - Multi-agent coordination

---

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, Error Handling table, Metrics, Execution Checklist, Best Practices Do/Don't, updated frontmatter with version/category/related_skills
- **1.0.0** (2025-12-30): Initial release based on Claude Code best practices

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [What is a Worktree?](what-is-a-worktree/SKILL.md)
- [Create a Worktree (+2)](create-a-worktree/SKILL.md)
- [Pattern 1: Feature + Review (+3)](pattern-1-feature-review/SKILL.md)
- [CLAUDE.md Configuration](claudemd-configuration/SKILL.md)
- [Headless Mode in Worktrees](headless-mode-in-worktrees/SKILL.md)
- [GitHub Actions Parallel Jobs](github-actions-parallel-jobs/SKILL.md)
