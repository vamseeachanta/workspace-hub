---
name: orcaflex-modeling-swarm-coordination
description: 'Sub-skill of orcaflex-modeling: Swarm Coordination (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Swarm Coordination (+1)

## Swarm Coordination


```javascript
// Initialize offshore analysis swarm
mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 5 }

// Spawn specialized agents
mcp__claude-flow__agent_spawn { type: "code-analyzer", name: "orcaflex-validator" }
mcp__claude-flow__agent_spawn { type: "tester", name: "simulation-verifier" }
```

## Memory Coordination


```javascript
// Store model configuration
mcp__claude-flow__memory_usage {
  action: "store",
  key: "orcaflex/model/config",
  namespace: "offshore",
  value: JSON.stringify({
    model: "mooring_analysis",
    status: "configured",
    timestamp: Date.now()

*See sub-skills for full details.*
