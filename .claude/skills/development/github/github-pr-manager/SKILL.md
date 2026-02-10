---
name: github-pr-manager
description: Comprehensive pull request management with swarm coordination for automated reviews, testing, and merge workflows. Use for PR lifecycle management, multi-reviewer coordination, conflict resolution, and intelligent branch management.
---

# GitHub PR Manager Skill

## Overview

Manage the complete pull request lifecycle with swarm coordination. This skill handles PR creation, multi-reviewer coordination, automated testing integration, conflict resolution, and intelligent merge strategies.

## Quick Start

```bash
# Check GitHub CLI authentication
gh auth status

# Create a PR with description
gh pr create --title "Feature: New API endpoint" --body "Implementation details..." --base main

# Review PR status
gh pr status

# List open PRs
gh pr list --state open
```

## When to Use

- Creating and managing pull requests
- Coordinating multi-reviewer workflows
- Resolving merge conflicts
- Automating PR testing and validation
- Managing branch synchronization
- Batch PR operations across repositories

## Core Capabilities

| Capability | Description |
|------------|-------------|
| Multi-reviewer coordination | Swarm agents for parallel code review |
| Automated conflict resolution | Intelligent merge strategies |
| Comprehensive testing | Integration with CI/CD validation |
| Real-time progress tracking | GitHub issue coordination |
| Branch management | Synchronization and cleanup |

## Usage Examples

### 1. Create PR with Swarm Coordination

```javascript
// Initialize review swarm

// Orchestrate review process
  task: "Complete PR review with testing and validation",
  strategy: "parallel",
  priority: "high"
})
```

### 2. Create and Manage PR with gh CLI

```bash
# Create PR
gh pr create \
  --repo owner/repo \
  --title "feat: Integration between packages" \
  --head feature-branch \
  --base main \
  --body "## Summary
- Added new integration
- Updated dependencies
- Fixed compatibility issues"

# View PR details
gh pr view 54 --json files,additions,deletions,title,body

# Add reviewers
gh pr edit 54 --add-reviewer user1,user2

# Check PR status
gh pr checks 54
```

### 3. Review and Approve PR

```bash
# Get PR diff
gh pr diff 54

# Approve PR
gh pr review 54 --approve --body "LGTM! All checks pass."

# Request changes
gh pr review 54 --request-changes --body "Please address the following..."

# Comment on PR
gh pr comment 54 --body "Consider refactoring this section."
```

### 4. Merge PR with Validation

```bash
# Check merge readiness
gh pr status

# Merge with squash
gh pr merge 54 --squash --delete-branch \
  --subject "feat: Complete integration" \
  --body "Comprehensive integration with swarm coordination"

# Merge with rebase
gh pr merge 54 --rebase --delete-branch
```

### 5. Batch PR Operations

```javascript
[Single Message - Complete PR Management]:
  // Initialize coordination

  // Create and manage PR
  Bash("gh pr create --repo owner/repo --title '...' --head '...' --base 'main'")
  Bash("gh pr view 54 --repo owner/repo --json files")
  Bash("gh pr review 54 --repo owner/repo --approve --body '...'")

  // Execute tests and validation
  Bash("npm test && npm run lint && npm run build")

  // Track progress
  TodoWrite({ todos: [
    { id: "review", content: "Complete code review", status: "completed" },
    { id: "test", content: "Run test suite", status: "completed" },
    { id: "merge", content: "Merge when ready", status: "pending" }
  ]})
```

## MCP Tool Integration

### Swarm Initialization

```javascript
    topology: "mesh",  // mesh, hierarchical, star, ring
    maxAgents: 4,
    strategy: "balanced"
})
```

### Agent Spawning

```javascript
    type: "reviewer",
    name: "PR Reviewer",
    capabilities: ["code-review", "security-audit", "performance-check"]
})
```

### Memory Coordination

```javascript
// Store PR state
    action: "store",
    key: "pr/54/status",
    value: JSON.stringify({
        timestamp: Date.now(),
        status: "approved",
        reviewers: ["user1", "user2"]
    })
})

// Retrieve PR state
    action: "retrieve",
    key: "pr/54/status"
})
```

## Best Practices

### 1. Always Use Swarm Coordination
- Initialize swarm before complex PR operations
- Assign specialized agents for different review aspects
- Use memory for cross-agent coordination

### 2. Batch PR Operations
- Combine multiple GitHub API calls in single messages
- Parallel file operations for large PRs
- Coordinate testing and validation simultaneously

### 3. Intelligent Review Strategy
- Automated conflict detection and resolution
- Multi-agent review for comprehensive coverage
- Performance and security validation integration

### 4. Progress Tracking
- Use TodoWrite for PR milestone tracking
- GitHub issue integration for project coordination
- Real-time status updates through swarm memory

## Error Handling

### Automatic retry logic for:
- Network failures during GitHub API calls
- Merge conflicts with intelligent resolution
- Test failures with automatic re-runs
- Review bottlenecks with load balancing

### Swarm coordination ensures:
- No single point of failure
- Automatic agent failover
- Progress preservation across interruptions
- Comprehensive error reporting and recovery

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `github-issue-tracker` | Link PRs to issues |
| `github-release-manager` | Coordinate release PRs |
| `github-code-review` | Detailed code analysis |
| `sparc-workflow` | SPARC development methodology |

## Hooks

### Pre-Task Hooks
```bash
gh auth status || (echo 'GitHub CLI not authenticated' && exit 1)
git status --porcelain
gh pr list --state open --limit 1 >/dev/null || echo 'No open PRs'
npm test --silent || echo 'Tests may need attention'
```

### Post-Task Hooks
```bash
gh pr status || echo 'No active PR in current branch'
git branch --show-current
gh pr checks || echo 'No PR checks available'
git log --oneline -3
```

---

## Version History

- **1.0.0** (2025-01-02): Initial release - converted from pr-manager agent
