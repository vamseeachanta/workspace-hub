---
name: github-multi-repo-swarm-coordination
description: 'Sub-skill of github-multi-repo: Swarm Coordination (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Swarm Coordination (+2)

## Swarm Coordination


```javascript
    topology: "hierarchical",
    maxAgents: 10,
    strategy: "balanced"
})

    repos: ["org/frontend", "org/backend", "org/shared"]
})
```

## Memory for Multi-Repo State


```javascript
    action: "store",
    key: "multi-repo/sync/status",
    namespace: "coordination",
    value: JSON.stringify({
        lastSync: Date.now(),
        repos: {
            frontend: { status: "synced", version: "2.0.0" },
            backend: { status: "synced", version: "2.1.0" },
            shared: { status: "synced", version: "1.5.0" }
        }
    })
})
```

## Metrics Collection


```javascript
    repos: ["org/frontend", "org/backend"],
    metrics: ["commits", "prs", "issues", "contributors"]
})
```
