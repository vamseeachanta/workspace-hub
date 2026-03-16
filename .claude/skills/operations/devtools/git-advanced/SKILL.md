---
name: git-advanced
version: 1.0.0
description: Advanced git workflows including rebase, worktrees, bisect, hooks, and
  monorepo patterns
author: workspace-hub
category: operations
capabilities:
- Interactive rebase and history rewriting
- Git worktrees for parallel development
- Bisect for bug hunting
- Rerere for conflict resolution
- Reflog for recovery
- Hooks and custom commands
- Submodules and monorepo patterns
tools:
- git
- gh
- git-lfs
- pre-commit
- husky
tags:
- git
- version-control
- rebase
- worktrees
- bisect
- hooks
- monorepo
platforms:
- linux
- macos
- windows
related_skills:
- docker
- cli-productivity
- github-actions
requires: []
see_also:
- git-advanced-1-interactive-rebase
- git-advanced-3-git-bisect
- git-advanced-6-git-hooks
- git-advanced-7-git-aliases
- git-advanced-9-monorepo-patterns
- git-advanced-1-complete-gitconfig
- git-advanced-1-commit-history
- git-advanced-common-issues
scripts_exempt: true
---

# Git Advanced

## When to Use This Skill

### USE when:

- Managing complex branch strategies
- Working on multiple features simultaneously
- Hunting down bugs with bisect
- Maintaining clean commit history
- Setting up team workflows with hooks
- Managing multi-repo dependencies
- Recovering from git mistakes
### DON'T USE when:

- Simple linear development (basic git suffices)
- Solo projects with simple history
- When team isn't familiar with advanced git
- Time-critical fixes (use simple commits)

## Prerequisites

### Installation

**Git Configuration:**
```bash
# Verify git version (2.23+ recommended)
git --version

# Global configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Recommended settings

*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Interactive rebase patterns
  - Git worktrees for parallel development
  - Bisect for bug hunting
  - Rerere and reflog for recovery
  - Hooks and custom commands
  - Submodules and monorepo patterns

---

**Use this skill to master advanced git workflows and maintain clean, professional version control!**

## Sub-Skills

- [1. Interactive Rebase (+1)](1-interactive-rebase/SKILL.md)
- [3. Git Bisect (+2)](3-git-bisect/SKILL.md)
- [6. Git Hooks](6-git-hooks/SKILL.md)
- [7. Git Aliases (+1)](7-git-aliases/SKILL.md)
- [9. Monorepo Patterns](9-monorepo-patterns/SKILL.md)
- [1. Complete .gitconfig (+2)](1-complete-gitconfig/SKILL.md)
- [1. Commit History (+2)](1-commit-history/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
