---
name: github-release-manager-swarm-coordination
description: 'Sub-skill of github-release-manager: Swarm Coordination (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Swarm Coordination (+1)

## Swarm Coordination


```javascript
    topology: "hierarchical",
    maxAgents: 6,
    strategy: "sequential"  // Release stages run in order
})
```

## Memory for Release State


```javascript
// Store release state
    action: "store",
    key: "release/v1.0.72/state",
    namespace: "releases",
    value: JSON.stringify({
        version: "1.0.72",
        stage: "testing",
        timestamp: Date.now()
    })
})
```
