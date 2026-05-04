---
name: github-swarm-pr
description: Pull request swarm management for multi-agent code review and validation.
  Use for coordinated PR reviews, automated validation, PR-based swarm creation, and
  intelligent merge workflows.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
---

# Github Swarm Pr

## Overview

This skill enables creation and management of AI swarms directly from GitHub Pull Requests, providing multi-agent code review, automated validation, and intelligent merge coordination. It transforms PRs into coordinated swarm workflows.

**Key Capabilities:**
- PR-based swarm creation with automatic agent assignment
- Multi-agent code review and validation
- PR comment commands for swarm control
- Automated PR lifecycle management
- Intelligent merge coordination with consensus

## Quick Start

```bash
# Get PR details for swarm initialization
gh pr view 123 --json title,body,labels,files,reviews

# Get PR diff for analysis
gh pr diff 123

# Check PR status
gh pr checks 123

# Review PR with swarm-generated feedback
gh pr review 123 --comment --body "## Swarm Analysis
- Code quality: PASS
- Test coverage: 85%
- Security: No issues found"
```

## When to Use

- **Complex PRs**: Large changes requiring multi-perspective review
- **Security Reviews**: PRs touching sensitive code paths
- **Architecture Changes**: Structural modifications needing architect review
- **Performance-Critical**: Changes to performance-sensitive code
- **Cross-Team PRs**: Changes affecting multiple team domains

## Related Skills

- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue-based swarm coordination
- [github-workflow](../github-workflow/SKILL.md) - CI/CD automation
- [github-sync](../github-sync/SKILL.md) - Repository synchronization
- [github-modes](../github-modes/SKILL.md) - GitHub integration modes

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from swarm-pr agent

## Sub-Skills

- [1. PR-Based Swarm Creation (+7)](1-pr-based-swarm-creation/SKILL.md)
- [1. PR Templates for Swarm](1-pr-templates-for-swarm/SKILL.md)

## Sub-Skills

- [Merge Status (+2)](merge-status/SKILL.md)
- [Automatic Agent Assignment (+1)](automatic-agent-assignment/SKILL.md)
- [Multi-Agent PR Coordination (+1)](multi-agent-pr-coordination/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [Summary](summary/SKILL.md)
- [Swarm Configuration](swarm-configuration/SKILL.md)
- [Tasks for Swarm](tasks-for-swarm/SKILL.md)
- [2. Status Checks (+1)](2-status-checks/SKILL.md)
- [Metrics and Reporting](metrics-and-reporting/SKILL.md)
