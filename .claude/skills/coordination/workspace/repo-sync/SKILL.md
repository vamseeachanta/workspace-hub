---
name: workspace-repo-sync
description: Manage and synchronize multiple Git repositories across workspace-hub.
  Use for bulk git operations, repository status checks, branch management, and coordinated
  commits across 26+ repositories.
version: 1.2.0
category: coordination
type: skill
capabilities:
- bulk_git_operations
- repository_status_monitoring
- branch_management
- coordinated_commits
- multi_repo_sync
tools:
- Bash
- Read
- Write
related_skills:
- workspace-cli
- compliance-check
- sparc-workflow
requires: []
see_also:
- workspace-repo-sync-common-commands
- workspace-repo-sync-work-repositories
- workspace-repo-sync-1-status-check
- workspace-repo-sync-list-branches
- workspace-repo-sync-daily-development-workflow
- workspace-repo-sync-selective-operations
- workspace-repo-sync-execution-checklist
- workspace-repo-sync-merge-conflicts
- workspace-repo-sync-metrics-success-criteria
- workspace-repo-sync-with-workspace-cli
- workspace-repo-sync-path-issues
tags: []
---

# Workspace Repo Sync

## Quick Start

```bash
# Check status of all repositories
./scripts/repository_sync status all

# Pull latest from all repos
./scripts/repository_sync pull all

# Sync (commit + push) all work repos
./scripts/repository_sync sync work -m "End of day sync"
```

## When to Use

- Starting a work session and need to pull latest changes across all repos
- End of day sync to commit and push all pending changes
- Checking which repos have uncommitted changes or are behind remote
- Coordinating branch changes across multiple related repositories
- Releasing updates across the entire workspace ecosystem

## Prerequisites

- Git installed and configured with SSH keys
- Access to all repositories in workspace-hub
- `./scripts/repository_sync` script available and executable
- Repository URLs configured in `config/repos.conf`

## Overview

This skill enables efficient management of multiple Git repositories in the workspace-hub ecosystem. It provides tools for bulk operations, status monitoring, and coordinated synchronization across all repositories.

## References

- [Workspace CLI Documentation](../docs/modules/cli/WORKSPACE_CLI.md)
- [Repository Sync Documentation](../docs/modules/cli/REPOSITORY_SYNC.md)
- [Development Workflow](../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

## Version History

- **1.2.0** (2026-02-12): Added MINGW root path, stash handling, divergence detection from /insights analysis of 65+ sync sessions
- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling consolidation, Metrics, Integration Points
- **1.0.0** (2024-10-15): Initial release with bulk operations, branch management, workflows, error handling, workspace integration

## Sub-Skills

- [Repository URLs (+2)](repository-urls/SKILL.md)
- [Commit Messages (+2)](commit-messages/SKILL.md)

## Sub-Skills

- [Common Commands](common-commands/SKILL.md)
- [Work Repositories (+2)](work-repositories/SKILL.md)
- [1. Status Check (+4)](1-status-check/SKILL.md)
- [List Branches (+3)](list-branches/SKILL.md)
- [Daily Development Workflow (+2)](daily-development-workflow/SKILL.md)
- [Selective Operations (+1)](selective-operations/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Merge Conflicts (+5)](merge-conflicts/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [With Workspace CLI (+2)](with-workspace-cli/SKILL.md)
- [Path Issues (+6)](path-issues/SKILL.md)
