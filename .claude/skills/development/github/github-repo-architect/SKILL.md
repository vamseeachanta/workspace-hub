---
name: github-repo-architect
description: Repository structure optimization and multi-repo management with swarm
  coordination for scalable project architecture and development workflows. Use for
  structure analysis, template management, cross-repo synchronization, and architecture
  recommendations.
capabilities: []
requires: []
see_also:
- github-repo-architect-core-capabilities
- github-repo-architect-1-repository-structure-analysis
- github-repo-architect-4-cross-repository-synchronization
- github-repo-architect-monorepo-structure
- github-repo-architect-swarm-coordination
- github-repo-architect-architecture-health-metrics
- github-repo-architect-integration-with-other-skills
tags: []
category: development
version: 1.0.0
---

# Github Repo Architect

## Overview

Repository structure optimization with swarm coordination. This skill handles repository structure analysis, template management, cross-repository synchronization, architecture recommendations, and development workflow optimization.

## Quick Start

```bash
# List repository structure
ls -la

# Search repositories in organization
gh repo list org --limit 20 --json name,description,languages

# Create new repository
gh repo create my-new-repo --public --description "Description"

# Clone repository
gh repo clone owner/repo

# View repository info
gh repo view owner/repo --json name,description,topics
```

## When to Use

- Analyzing repository structure for optimization
- Creating standardized project templates
- Cross-repository synchronization
- Architecture analysis and recommendations
- Multi-repo workflow coordination

## Quick Start

```bash
npm install
```

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from repo-architect agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Core Capabilities](core-capabilities/SKILL.md)
- [1. Repository Structure Analysis (+2)](1-repository-structure-analysis/SKILL.md)
- [4. Cross-Repository Synchronization (+1)](4-cross-repository-synchronization/SKILL.md)
- [Monorepo Structure (+2)](monorepo-structure/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [Architecture Health Metrics (+1)](architecture-health-metrics/SKILL.md)
- [Integration with Other Skills](integration-with-other-skills/SKILL.md)
