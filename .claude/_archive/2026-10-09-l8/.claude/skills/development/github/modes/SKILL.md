---
name: github-modes
description: Comprehensive GitHub integration modes for workflow orchestration, PR
  management, and repository coordination. Use for GitHub CLI operations, automated
  workflows, PR reviews, issue tracking, release management, and CI/CD coordination.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
---

# Github Modes

## Overview

This skill provides comprehensive GitHub integration modes for workflow orchestration, PR management, issue tracking, and repository coordination. Each mode is optimized for specific GitHub workflows with batch operation support.

**Key Capabilities:**
- GitHub workflow orchestration and coordination
- Pull request management and review automation
- Issue tracking and project management
- Release coordination and deployment
- Repository architecture and organization
- CI/CD pipeline coordination

## Quick Start

```bash
# Verify GitHub CLI authentication
gh auth status

# Check repository access
gh repo view

# List open PRs
gh pr list

# List issues
gh issue list

# Check workflow runs
gh run list --limit 5
```

## Related Skills

- [github-sync](../github-sync/SKILL.md) - Repository synchronization
- [github-workflow](../github-workflow/SKILL.md) - CI/CD automation
- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR swarm management
- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue swarm coordination
- [github-project-board](../github-project-board/SKILL.md) - Project board sync

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from github-modes agent

## Sub-Skills

- [Complete PR Workflow](complete-pr-workflow/SKILL.md)
- [1. Authentication (+3)](1-authentication/SKILL.md)

## Sub-Skills

- [1. gh-coordinator (+3)](1-gh-coordinator/SKILL.md)
- [5. repo-architect (+2)](5-repo-architect/SKILL.md)
- [8. sync-coordinator (+2)](8-sync-coordinator/SKILL.md)
- [Batch Operations](batch-operations/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [Automated Issue Management](automated-issue-management/SKILL.md)
- [Configuration Options](configuration-options/SKILL.md)
