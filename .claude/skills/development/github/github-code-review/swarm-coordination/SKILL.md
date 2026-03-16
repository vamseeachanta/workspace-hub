---
name: github-code-review-swarm-coordination
description: 'Sub-skill of github-code-review: Swarm Coordination (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Swarm Coordination (+1)

## Swarm Coordination


```javascript
// Initialize review swarm
    topology: "hierarchical",
    maxAgents: 5,
    strategy: "specialized"
})

// Spawn specialized reviewers
    agents: [
        { type: "reviewer", name: "security-agent", capabilities: ["security-audit"] },
        { type: "reviewer", name: "perf-agent", capabilities: ["performance-analysis"] },
        { type: "reviewer", name: "style-agent", capabilities: ["code-style"] }
    ]
})
```

## Memory for Review State


```javascript
// Store review findings
    action: "store",
    key: "review/pr-123/findings",
    value: JSON.stringify({
        security: { issues: 2, severity: "medium" },
        performance: { issues: 1, severity: "low" },
        style: { issues: 5, severity: "info" }
    })
})
```
