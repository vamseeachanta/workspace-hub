---
name: github-swarm-issue
description: GitHub issue-based swarm coordination for intelligent task decomposition
  and progress tracking. Use for transforming issues into multi-agent tasks, automated
  triage, task breakdown, and issue lifecycle management.
capabilities: []
requires: []
see_also:
- github-swarm-issue-swarm-task-breakdown
- github-swarm-issue-task
- github-swarm-issue-3-progress-tracking
- github-swarm-issue-issue-templates-for-swarms
- github-swarm-issue-multi-agent-issue-processing
- github-swarm-issue-github-actions-integration
- github-swarm-issue-bug-reports
- github-swarm-issue-metrics-and-analytics
tags: []
category: development
version: 1.0.0
---

# Github Swarm Issue

## Overview

This skill transforms GitHub Issues into intelligent swarm tasks, enabling automatic task decomposition, agent coordination, and comprehensive progress tracking. It provides issue-to-swarm conversion, automated triage, and lifecycle management.

**Key Capabilities:**
- Issue-to-swarm conversion with automatic decomposition
- Issue comment commands for swarm control
- Automated triage and labeling
- Task breakdown with subtask creation
- Progress tracking with visual updates
- Duplicate detection and linking

## Quick Start

```bash
# Get issue details for swarm initialization
gh issue view 456 --json title,body,labels,assignees,comments

# List issues ready for swarm processing
gh issue list --label "swarm-ready"

# Add swarm label to trigger processing
gh issue edit 456 --add-label "swarm-ready"

# Post swarm status comment
gh issue comment 456 --body "Swarm initialized for this issue"
```

## When to Use

- **Complex Issues**: Multi-step tasks requiring decomposition
- **Bug Investigation**: Issues needing systematic debugging
- **Feature Requests**: New features requiring architecture and implementation
- **Technical Debt**: Refactoring tasks with multiple components
- **Epic Management**: Coordinating child issues under parent

## Related Skills

- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR-based swarm coordination
- [github-project-board](../github-project-board/SKILL.md) - Project board integration
- [github-workflow](../github-workflow/SKILL.md) - CI/CD automation
- [github-modes](../github-modes/SKILL.md) - GitHub integration modes

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from swarm-issue agent

## Sub-Skills

- [1. Issue-to-Swarm Conversion (+1)](1-issue-to-swarm-conversion/SKILL.md)
- [1. Issue Templates (+3)](1-issue-templates/SKILL.md)

## Sub-Skills

- [Swarm Task Breakdown](swarm-task-breakdown/SKILL.md)
- [Task](task/SKILL.md)
- [3. Progress Tracking (+3)](3-progress-tracking/SKILL.md)
- [Issue Templates for Swarms](issue-templates-for-swarms/SKILL.md)
- [Multi-Agent Issue Processing (+1)](multi-agent-issue-processing/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [Bug Reports (+1)](bug-reports/SKILL.md)
- [Metrics and Analytics](metrics-and-analytics/SKILL.md)
