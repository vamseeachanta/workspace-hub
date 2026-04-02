---
name: github-multi-repo
description: Cross-repository swarm orchestration for organization-wide automation
  and intelligent collaboration. Use for multi-repo coordination, synchronized operations,
  dependency management, and organization-wide policy changes.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
---

# Github Multi Repo

## Overview

Cross-repository swarm orchestration for organization-wide automation. This skill handles multi-repo coordination, synchronized operations, dependency management, security updates, and organization-wide policy changes.

## Quick Start

```bash
# List organization repositories
gh repo list org --limit 100 --json name,description,languages

# Search across repositories
gh search code "pattern" --repo org/repo1 --repo org/repo2

# Clone multiple repos
for repo in repo1 repo2 repo3; do
  gh repo clone org/$repo
done

# Check repository info
gh api repos/org/repo --jq '{name, default_branch, languages, topics}'
```

## When to Use

- Coordinating changes across multiple repositories
- Organization-wide dependency updates
- Synchronized security patches
- Cross-repo refactoring operations
- Multi-service microservices coordination
- Library updates across consumers

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from multi-repo-swarm agent

## Sub-Skills

- [Core Capabilities](core-capabilities/SKILL.md)
- [1. Cross-Repo Swarm Initialization (+4)](1-cross-repo-swarm-initialization/SKILL.md)
- [1. Repository Organization (+2)](1-repository-organization/SKILL.md)
- [Connectivity Issues (+1)](connectivity-issues/SKILL.md)

## Sub-Skills

- [Multi-Repo Configuration](multi-repo-configuration/SKILL.md)
- [Eventually Consistent (+2)](eventually-consistent/SKILL.md)
- [Swarm Coordination (+2)](swarm-coordination/SKILL.md)
- [Microservices Coordination (+2)](microservices-coordination/SKILL.md)
- [Multi-Repo Dashboard (+2)](multi-repo-dashboard/SKILL.md)
