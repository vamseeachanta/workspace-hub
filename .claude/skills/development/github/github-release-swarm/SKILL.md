---
name: github-release-swarm
description: Orchestrate complex software releases using AI swarms that handle everything
  from changelog generation to multi-platform deployment. Use for release planning,
  automated versioning, artifact building, progressive deployment, and multi-repo
  releases.
capabilities: []
requires: []
see_also:
- github-release-swarm-release-agents
- github-release-swarm-1-release-planning
- github-release-swarm-release-configuration
- github-release-swarm-progressive-deployment
- github-release-swarm-swarm-coordination
- github-release-swarm-github-actions-workflow
- github-release-swarm-hotfix-process
tags: []
category: development
version: 1.0.0
---

# Github Release Swarm

## Overview

Orchestrate complex software releases using AI swarms. This skill handles release planning, automated versioning, changelog generation, artifact building, progressive deployment, and multi-repo release coordination.

## Quick Start

```bash
# Get last release tag
LAST_TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')

# Get commits since last release
gh api repos/owner/repo/compare/${LAST_TAG}...HEAD --jq '.commits[].commit.message'

# Get merged PRs since last release
gh pr list --state merged --base main --json number,title,labels,mergedAt

# Create release
gh release create v2.0.0 --title "Release v2.0.0" --notes "..."
```

## When to Use

- Planning and coordinating major releases
- Automated changelog generation
- Multi-platform artifact building
- Progressive deployment strategies
- Multi-repository release coordination
- Hotfix automation

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from release-swarm agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Release Agents](release-agents/SKILL.md)
- [1. Release Planning (+4)](1-release-planning/SKILL.md)
- [Release Configuration](release-configuration/SKILL.md)
- [Progressive Deployment](progressive-deployment/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [GitHub Actions Workflow](github-actions-workflow/SKILL.md)
- [Hotfix Process (+1)](hotfix-process/SKILL.md)
