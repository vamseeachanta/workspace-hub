---
name: github-code-review
description: Deploy specialized AI agents to perform comprehensive, intelligent code
  reviews that go beyond traditional static analysis. Use for automated multi-agent
  review, security vulnerability analysis, performance bottleneck detection, and architecture
  pattern validation.
capabilities: []
requires: []
see_also:
- github-code-review-security-agent
- github-code-review-1-multi-agent-review-system
- github-code-review-review-configuration
- github-code-review-swarm-coordination
- github-code-review-github-actions-integration
- github-code-review-security-issue
tags: []
category: development
version: 1.0.0
---

# Github Code Review

## Overview

Deploy specialized AI agents for comprehensive code reviews. This skill provides multi-agent review capabilities covering security vulnerabilities, performance bottlenecks, architecture patterns, and code style enforcement.

## Quick Start

```bash
# Get PR details for review
gh pr view 123 --json files,additions,deletions,title,body

# Get PR diff
gh pr diff 123

# Post review comment
gh pr review 123 --comment --body "Review findings..."

# Approve PR
gh pr review 123 --approve --body "LGTM!"

# Request changes
gh pr review 123 --request-changes --body "Please fix..."
```

## When to Use

- Automated code review for pull requests
- Security vulnerability analysis
- Performance bottleneck detection
- Architecture pattern validation
- Style and convention enforcement
- Multi-agent collaborative review

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from code-review-swarm agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Security Agent (+3)](security-agent/SKILL.md)
- [1. Multi-Agent Review System (+3)](1-multi-agent-review-system/SKILL.md)
- [Review Configuration](review-configuration/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [Security Issue (+1)](security-issue/SKILL.md)
