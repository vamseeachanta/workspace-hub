---
name: agent-orchestration-topology-selection
description: 'Sub-skill of agent-orchestration: Topology Selection (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Topology Selection (+2)

## Topology Selection


Choose topology based on task:

| Task Type | Recommended Topology |
|-----------|---------------------|
| Code review | Hierarchical |
| Brainstorming | Mesh |
| Pipeline processing | Ring |
| Centralized coordination | Star |
| Mixed workloads | Adaptive |

## Auto-Optimize


```javascript
```

## Load Balancing


```javascript
    swarmId: "current",
    tasks: ["task1", "task2", "task3"]
})
```
