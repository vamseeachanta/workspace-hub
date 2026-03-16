---
name: github-swarm-pr-multi-agent-pr-coordination
description: 'Sub-skill of github-swarm-pr: Multi-Agent PR Coordination (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Multi-Agent PR Coordination (+1)

## Multi-Agent PR Coordination


```javascript
// Initialize PR-specific swarm

// Store PR context in swarm memory
  action: "store",
  key: "pr/123/context",
  value: {
    pr_number: 123,
    files_changed: ["src/auth.js", "tests/auth.test.js"],
    complexity_score: 7.5,

*See sub-skills for full details.*

## Swarm-Coordinated Merge


```javascript
// Coordinate merge decision with swarm

// Analyze merge readiness
  task: "Evaluate PR merge readiness with comprehensive validation",
  strategy: "sequential",
  priority: "critical"
}

// Store merge decision

*See sub-skills for full details.*
