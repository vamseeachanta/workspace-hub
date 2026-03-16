---
name: github-project-board
description: Synchronize AI swarms with GitHub Projects for visual task management
  and progress tracking. Use for project board automation, task synchronization, sprint
  management, and team coordination with GitHub Projects.
capabilities: []
requires: []
see_also:
- github-project-board-status-mapping
- github-project-board-swarm-board-synchronization
- github-project-board-auto-assignment-rules
- github-project-board-generate-board-analytics
- github-project-board-summary
- github-project-board-status-distribution
- github-project-board-kpi-tracking
- github-project-board-configuration-options
tags: []
category: development
version: 1.0.0
---

# Github Project Board

## Overview

This skill enables synchronization between AI swarms and GitHub Projects for visual task management, progress tracking, and team coordination. It provides bidirectional sync, automated card management, and comprehensive project analytics.

**Key Capabilities:**
- Bidirectional sync between swarm tasks and project cards
- Automated card movement based on task status
- Real-time progress tracking and visualization
- Sprint management and velocity tracking
- Team workload distribution and analytics

## Quick Start

```bash
# List your GitHub Projects
gh project list --owner @me

# Get project ID
PROJECT_ID=$(gh project list --owner @me --format json | \
  jq -r '.projects[] | select(.title == "Development Board") | .number')

# Add an issue to the project
gh project item-add $PROJECT_ID --owner @me \
  --url "https://github.com/$REPO/issues/123"

# List project items
gh project item-list $PROJECT_ID --owner @me --format json
```

## When to Use

- **Task Visualization**: Creating visual boards for swarm tasks
- **Sprint Planning**: Managing sprints with automated tracking
- **Progress Tracking**: Real-time updates on task completion
- **Team Coordination**: Distributing work across team members
- **Reporting**: Generating analytics and status reports

## Related Skills

- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue-based coordination
- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR management
- [github-sync](../github-sync/SKILL.md) - Repository synchronization

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from project-board-sync agent

## Sub-Skills

- [1. Board Initialization (+3)](1-board-initialization/SKILL.md)
- [1. Board Organization (+3)](1-board-organization/SKILL.md)
- [Common Issues](common-issues/SKILL.md)

## Sub-Skills

- [Status Mapping (+1)](status-mapping/SKILL.md)
- [Swarm-Board Synchronization (+1)](swarm-board-synchronization/SKILL.md)
- [Auto-Assignment Rules (+1)](auto-assignment-rules/SKILL.md)
- [Generate Board Analytics](generate-board-analytics/SKILL.md)
- [Summary](summary/SKILL.md)
- [Status Distribution](status-distribution/SKILL.md)
- [KPI Tracking](kpi-tracking/SKILL.md)
- [Configuration Options](configuration-options/SKILL.md)
