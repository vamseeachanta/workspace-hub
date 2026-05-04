---
name: github-swarm-issue-bug-reports
description: 'Sub-skill of github-swarm-issue: Bug Reports (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Bug Reports (+1)

## Bug Reports


```bash
# Specialized bug handling
handle_bug() {
  local ISSUE_NUM=$1

  gh issue comment $ISSUE_NUM --body "## Bug Investigation Swarm

**Agents Assigned:**
- Debugger: Reproduce and isolate
- Analyst: Root cause analysis

*See sub-skills for full details.*

## Feature Requests


```bash
# Feature implementation workflow
handle_feature() {
  local ISSUE_NUM=$1

  gh issue comment $ISSUE_NUM --body "## Feature Implementation Swarm

**Agents Assigned:**
- Architect: Design approach
- Coder: Implementation

*See sub-skills for full details.*
