---
name: github-issue-tracker
description: Intelligent issue management and project coordination with automated
  tracking, progress monitoring, and team coordination. Use for issue creation with
  smart templates, progress tracking with swarm coordination, multi-agent collaboration,
  and cross-repository synchronization.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
---

# Github Issue Tracker

## Overview

Intelligent issue management with swarm coordination. This skill handles automated issue creation, progress tracking, multi-agent collaboration on complex issues, project milestone coordination, and cross-repository issue synchronization.

## Quick Start

```bash
# Create an issue
gh issue create --title "Bug: Login fails" --body "Steps to reproduce..." --label "bug"

# List open issues
gh issue list --state open

# View issue details
gh issue view 54

# Add comment to issue
gh issue comment 54 --body "Progress update..."

# Close issue
gh issue close 54 --reason completed
```

## When to Use

- Creating issues with smart templates
- Tracking issue progress with swarm coordination
- Multi-agent collaboration on complex issues
- Project milestone coordination
- Cross-repository issue synchronization
- Automated issue labeling and organization

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from issue-tracker agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Core Capabilities](core-capabilities/SKILL.md)
- [1. Create Issue with Swarm Tracking (+1)](1-create-issue-with-swarm-tracking/SKILL.md)
- [Objectives](objectives/SKILL.md)
- [3. Automated Progress Updates (+5)](3-automated-progress-updates/SKILL.md)
- [Integration Issue Template](integration-issue-template/SKILL.md)
- [Overview (+4)](overview/SKILL.md)
- [Problem Description (+6)](problem-description/SKILL.md)
- [Swarm Coordination (+1)](swarm-coordination/SKILL.md)
- [Integration with Other Skills](integration-with-other-skills/SKILL.md)
- [Automatic tracking of: (+1)](automatic-tracking-of/SKILL.md)
