---
name: agent-orchestration-simple-task
description: 'Sub-skill of agent-orchestration: Simple Task (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Simple Task (+2)

## Simple Task


```javascript
    task: "Implement user authentication with JWT",
    strategy: "sequential",
    priority: "high"
})
```

## Complex Task with Dependencies


```javascript
    task: "Build complete API with tests and documentation",
    strategy: "adaptive",
    priority: "high",
    dependencies: [
        "design-api-spec",
        "write-tests",
        "implement-endpoints",
        "create-documentation"
    ]
})
```

## Orchestration Strategies


| Strategy | Description |
|----------|-------------|
| `parallel` | Execute independent tasks simultaneously |
| `sequential` | Execute tasks in order |
| `adaptive` | Dynamically adjust based on results |
| `balanced` | Balance load across agents |
