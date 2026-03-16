---
name: agent-orchestration-agent-spawn-failures
description: 'Sub-skill of agent-orchestration: Agent Spawn Failures (+3).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Agent Spawn Failures (+3)

## Agent Spawn Failures


```javascript
// Check agent status after spawning
if (status.agents.length < expectedCount) {
    // Retry failed spawns
}
```

## Task Orchestration Failures


```javascript
// Use fault tolerance for critical tasks
    agentId: "agent-123",
    strategy: "restart"  // or "failover", "ignore"
})
```

## Recovery


```javascript
// Create snapshot before risky operations

// Restore if needed
```

## Swarm Coordination Issues


- **Topology mismatch**: Choose topology based on task structure
- **Agent overload**: Scale down or use load balancing
- **Memory conflicts**: Use namespaced memory storage
- **Timeout issues**: Set reasonable timeouts, monitor progress
