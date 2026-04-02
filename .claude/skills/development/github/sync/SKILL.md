---
name: github-sync
description: Multi-repository synchronization coordinator for version alignment, dependency
  sync, and cross-package integration. Use for package synchronization, version management,
  documentation alignment, and coordinated releases across multiple repositories.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
freedom: low
---

# Github Sync

## Overview

This skill enables multi-package synchronization and version alignment across repositories with intelligent swarm coordination. It manages dependency resolution, documentation consistency, and cross-package integration for seamless multi-repository workflows.

**Key Capabilities:**
- Package dependency synchronization with conflict resolution
- Version alignment across multiple repositories
- Cross-package integration with automated testing
- Documentation synchronization for consistency
- Release coordination with deployment pipelines

## Quick Start

```bash
# Synchronize package dependencies across repos
gh api repos/:owner/:repo1/contents/package.json --jq '.content' | base64 -d > /tmp/pkg1.json
gh api repos/:owner/:repo2/contents/package.json --jq '.content' | base64 -d > /tmp/pkg2.json

# Compare and identify version differences
diff -u /tmp/pkg1.json /tmp/pkg2.json

# Create sync branch
gh api repos/:owner/:repo/git/refs \
  -f ref='refs/heads/sync/package-alignment' \
  -f sha=$(gh api repos/:owner/:repo/git/refs/heads/main --jq '.object.sha')
```

## When to Use

- **Package Synchronization**: Aligning versions across monorepo packages
- **Dependency Updates**: Coordinating major dependency upgrades
- **Documentation Sync**: Keeping README/CLAUDE.md files consistent
- **Release Coordination**: Managing synchronized releases
- **Cross-Repo Features**: Implementing features spanning multiple packages

## Related Skills

- [github-workflow](../github-workflow/SKILL.md) - CI/CD pipeline automation
- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR management with swarms
- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue-based coordination

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from sync-coordinator agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [1. Synchronize Package Dependencies (+4)](1-synchronize-package-dependencies/SKILL.md)
- [Swarm-Coordinated Sync (+1)](swarm-coordinated-sync/SKILL.md)
- [Version Alignment Strategy (+1)](version-alignment-strategy/SKILL.md)
- [Sync Quality Metrics (+1)](sync-quality-metrics/SKILL.md)
