---
name: github-pr-manager-best-practices
description: 'Sub-skill of github-pr-manager: Best Practices.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

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
