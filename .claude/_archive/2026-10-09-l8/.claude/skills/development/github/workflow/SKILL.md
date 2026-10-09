---
name: github-workflow
description: GitHub Actions workflow automation for intelligent CI/CD pipelines with
  adaptive optimization. Use for workflow creation, pipeline optimization, security
  scanning, failure analysis, and automated deployment strategies.
type: reference
capabilities: []
requires: []
tags: []
category: development
version: 1.0.0
---

# Github Workflow

## Overview

This skill enables creation and management of intelligent, self-organizing CI/CD pipelines using GitHub Actions with swarm coordination. It provides adaptive workflow generation, performance optimization, and automated pipeline management.

**Key Capabilities:**
- Swarm-powered GitHub Actions workflows
- Dynamic workflow generation based on code analysis
- Intelligent test selection and parallelization
- Self-healing pipeline automation
- Performance monitoring and optimization

## Quick Start

```yaml
# .github/workflows/intelligent-ci.yml
name: Intelligent CI with Swarms
on: [push, pull_request]

jobs:
  analyze-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Analyze Changes
        run: |
          # Determine affected packages
          CHANGED=$(git diff --name-only HEAD~1)
          echo "Changed files: $CHANGED"

      - name: Dynamic Test Selection
        run: |
          # Run only affected tests
          npm test -- --changedSince=HEAD~1
```

## When to Use

- **New Project Setup**: Creating initial CI/CD pipelines
- **Pipeline Optimization**: Improving slow or inefficient workflows
- **Security Integration**: Adding automated security scanning
- **Deployment Automation**: Setting up progressive deployment strategies
- **Failure Recovery**: Implementing self-healing pipelines

## Usage Examples

### 1. Multi-Language Detection Workflow

```yaml
# .github/workflows/polyglot-ci.yml
name: Polyglot Project Handler
on: push

jobs:
  detect-and-build:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.detect.outputs.matrix }}

*See sub-skills for full details.*
### 2. Adaptive Security Scanning

```yaml
# .github/workflows/security-scan.yml
name: Intelligent Security Scan
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  security-analysis:

*See sub-skills for full details.*
### 3. Self-Healing Pipeline

```yaml
# .github/workflows/self-healing.yml
name: Self-Healing Pipeline
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  heal-pipeline:

*See sub-skills for full details.*
### 4. Progressive Deployment

```yaml
# .github/workflows/progressive-deploy.yml
name: Progressive Deployment
on:
  push:
    branches: [main]

jobs:
  analyze-risk:
    runs-on: ubuntu-latest

*See sub-skills for full details.*

## MCP Tool Integration

### Multi-Agent Pipeline Orchestration

```javascript
// Initialize workflow automation swarm

// Create automation rules
  rules: [
    {
      trigger: "pull_request",
      conditions: ["files_changed > 10", "complexity_high"],
      actions: ["spawn_review_swarm", "parallel_testing", "security_scan"]
    },

*See sub-skills for full details.*
### Performance Monitoring

```javascript
// Generate workflow performance reports
  format: "detailed",
  timeframe: "30d"
}

// Analyze bottlenecks
  component: "github_actions_workflow",
  metrics: ["build_time", "test_duration", "deployment_latency"]
}

*See sub-skills for full details.*

## Workflow Optimization Commands

### Pipeline Optimization

```bash
# Analyze workflow performance
gh run list --workflow=ci.yml --limit=20 --json databaseId,conclusion,startedAt,updatedAt | \
  jq 'map({id: .databaseId, status: .conclusion, duration: ((.updatedAt | fromdateiso8601) - (.startedAt | fromdateiso8601))})'

# Identify slow steps
gh run view $RUN_ID --json jobs --jq '.jobs[] | {name: .name, duration: .steps | map(.completedAt | fromdateiso8601) | max - (.steps | map(.startedAt | fromdateiso8601) | min)}'
```
### Failure Analysis

```bash
# Analyze failed runs
gh run list --status=failure --limit=10 --json databaseId,name,headBranch | \
  jq -r '.[] | "\(.databaseId): \(.name) on \(.headBranch)"'

# Get failure details
gh run view $RUN_ID --log-failed
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max-parallel | number | 4 | Maximum parallel jobs |
| timeout-minutes | number | 30 | Job timeout |
| retry-on-failure | boolean | false | Auto-retry failed jobs |
| cache-strategy | string | "npm" | Dependency caching |

## Related Skills

- [github-sync](../github-sync/SKILL.md) - Repository synchronization
- [github-swarm-pr](../github-swarm-pr/SKILL.md) - PR management
- [github-swarm-issue](../github-swarm-issue/SKILL.md) - Issue coordination

---

## Version History

- **1.0.0** (2026-01-02): Initial skill conversion from workflow-automation agent

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
