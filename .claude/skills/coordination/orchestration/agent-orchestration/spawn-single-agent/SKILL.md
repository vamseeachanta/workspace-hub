---
name: agent-orchestration-spawn-single-agent
description: 'Sub-skill of agent-orchestration: Spawn Single Agent (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Spawn Single Agent (+2)

## Spawn Single Agent


```javascript
    type: "coder",
    name: "implementation-agent",
    capabilities: ["python", "typescript", "api-development"]
})
```

## Spawn Multiple Agents in Parallel


```javascript
    agents: [
        { type: "coder", name: "backend-coder" },
        { type: "tester", name: "test-writer" },
        { type: "reviewer", name: "code-reviewer" }
    ],
    maxConcurrency: 3
})
```

## Agent Types


```javascript
// Available agent types
const agentTypes = [
    "coordinator",
    "analyst",
    "optimizer",
    "documenter",
    "monitor",
    "specialist",
    "architect",

*See sub-skills for full details.*
