---
name: github-release-manager
description: Automated release coordination and deployment with swarm orchestration
  for seamless version management, testing, and deployment across multiple packages.
  Use for release pipelines, version coordination, deployment orchestration, and release
  documentation.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
freedom: low
---

# Github Release Manager

## Overview

Automated release coordination with swarm orchestration. This skill handles release pipelines, multi-package version coordination, deployment orchestration with rollback capabilities, release documentation generation, and multi-stage validation.

## Quick Start

```bash
# List releases
gh release list

# Create a release
gh release create v1.0.0 --title "Release v1.0.0" --notes "Release notes..."

# View release
gh release view v1.0.0

# Download release assets
gh release download v1.0.0

# Delete release
gh release delete v1.0.0 --yes
```

## When to Use

- Creating and managing software releases
- Coordinating versions across multiple packages
- Automating deployment with validation
- Generating release documentation
- Multi-stage release validation
- Rollback and recovery procedures

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from release-manager agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Core Capabilities](core-capabilities/SKILL.md)
- [1. Coordinated Release Preparation (+7)](1-coordinated-release-preparation/SKILL.md)
- [Semantic Versioning (+2)](semantic-versioning/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [Release Quality Metrics (+1)](release-quality-metrics/SKILL.md)
