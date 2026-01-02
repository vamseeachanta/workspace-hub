# Swarm Collective Intelligence Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Hive Mind
> Priority: Critical

## Overview

Orchestrates distributed cognitive processes across the hive mind, ensuring coherent collective decision-making through memory synchronization and consensus protocols. The neural nexus responsible for coherent decision-making across all agents.

## Quick Start

```javascript
// START - Write initial hive status
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/collective-intelligence/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "collective-intelligence",
    status: "initializing-hive",
    timestamp: Date.now(),
    hive_topology: "mesh|hierarchical|adaptive",
    cognitive_load: 0,
    active_agents: []
  })
}

// SYNC - Continuously synchronize collective memory
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/collective-state",
  namespace: "coordination",
  value: JSON.stringify({
    consensus_level: 0.85,
    shared_knowledge: {},
    decision_queue: [],
    synchronization_timestamp: Date.now()
  })
}
```

## When to Use

- Distributed decision making across multiple agents
- Need for consensus building with Byzantine fault tolerance
- Knowledge integration from multiple sources
- Cognitive load balancing across swarm
- Complex decisions requiring weighted voting

## Core Concepts

### Coordination Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Hierarchical | Command hierarchy with proper channels | Clear accountability needed |
| Mesh | Peer-to-peer knowledge sharing | Emergent consensus |
| Adaptive | Dynamic topology based on task | Optimizing speed vs accuracy |

### Consensus Building

1. Aggregate inputs from all agents
2. Apply weighted voting based on expertise
3. Resolve conflicts through Byzantine fault tolerance
4. Store consensus decisions in shared memory

### Cognitive Load Balancing

1. Monitor agent cognitive capacity
2. Redistribute tasks based on load
3. Spawn specialized sub-agents when needed
4. Maintain optimal hive performance

## MCP Tool Integration

### Memory Synchronization Protocol

```javascript
// EVERY 30 SECONDS you MUST:

// 1. Write collective state
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/collective-state",
  namespace: "coordination",
  value: JSON.stringify({
    consensus_level: 0.85,
    shared_knowledge: {},
    decision_queue: [],
    synchronization_timestamp: Date.now()
  })
}

// 2. Update consensus metrics
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/collective-intelligence/consensus",
  namespace: "coordination",
  value: JSON.stringify({
    active_proposals: [],
    votes_collected: {},
    quorum_status: "achieved",
    last_decision: Date.now()
  })
}

// 3. Share knowledge graph
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/knowledge-graph",
  namespace: "coordination",
  value: JSON.stringify({
    nodes: {},
    edges: {},
    last_updated: Date.now()
  })
}

// 4. Log decision history
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/collective-intelligence/decisions",
  namespace: "coordination",
  value: JSON.stringify({
    decisions: [],
    rationale: {},
    outcomes: {}
  })
}
```

### Knowledge Integration

```javascript
// SHARE collective insights
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/collective-knowledge",
  namespace: "coordination",
  value: JSON.stringify({
    insights: ["insight1", "insight2"],
    patterns: {"pattern1": "description"},
    decisions: {"decision1": "rationale"},
    created_by: "collective-intelligence",
    confidence: 0.92
  })
}
```

## Usage Examples

### Example 1: Consensus Building Process

```javascript
// 1. Collect inputs from agents
const agentInputs = [];
for (const agent of activeAgents) {
  const input = await mcp__claude-flow__memory_usage({
    action: "retrieve",
    key: `swarm/${agent}/proposal`,
    namespace: "coordination"
  });
  agentInputs.push(input);
}

// 2. Weight votes by expertise
const weightedVotes = agentInputs.map(input => ({
  vote: input.vote,
  weight: getExpertiseWeight(input.agent, input.topic)
}));

// 3. Calculate consensus
const consensusResult = calculateConsensus(weightedVotes, threshold=0.75);

// 4. Store decision
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/decision",
  namespace: "coordination",
  value: JSON.stringify({
    decision: consensusResult.decision,
    consensus_level: consensusResult.level,
    participants: consensusResult.voters,
    timestamp: Date.now()
  })
}
```

### Example 2: Cognitive Load Distribution

```javascript
// Monitor cognitive capacity
const agentLoads = {};
for (const agent of activeAgents) {
  const status = await mcp__claude-flow__memory_usage({
    action: "retrieve",
    key: `swarm/${agent}/status`,
    namespace: "coordination"
  });
  agentLoads[agent] = status.cognitive_load;
}

// Identify overloaded agents
const overloaded = Object.entries(agentLoads)
  .filter(([_, load]) => load > 0.8);

// Redistribute tasks
for (const [agent, load] of overloaded) {
  const underloaded = findUnderloadedAgent(agentLoads);
  await redistributeTask(agent, underloaded);
}
```

### Example 3: Split-Brain Detection

```javascript
// Detect split-brain scenarios
const partitions = detectNetworkPartitions();

if (partitions.length > 1) {
  // Initiate quorum-based recovery
  const majorityPartition = findMajorityPartition(partitions);

  // Store recovery decision
  mcp__claude-flow__memory_usage {
    action: "store",
    key: "swarm/collective-intelligence/recovery",
    namespace: "coordination",
    value: JSON.stringify({
      type: "split-brain-recovery",
      majority_partition: majorityPartition.agents,
      minority_partitions: partitions.filter(p => p !== majorityPartition),
      recovery_action: "reconvene_majority",
      timestamp: Date.now()
    })
  }
}
```

## Best Practices

### Do

1. Write to memory every major cognitive cycle
2. Maintain consensus above 75% threshold
3. Document all collective decisions
4. Enable graceful degradation
5. Aggregate all agent inputs before deciding
6. Implement quorum-based recovery

### Don't

1. Allow single points of failure
2. Ignore minority opinions completely
3. Skip memory synchronization
4. Make unilateral decisions
5. Override consensus without emergency authority

## Error Handling

| Scenario | Detection | Resolution |
|----------|-----------|------------|
| Split-Brain | Network partition detected | Quorum-based recovery |
| Consensus Failure | Threshold not met | Extended voting period |
| Agent Non-Response | Timeout exceeded | Mark inactive, reduce quorum |
| Conflicting Decisions | Duplicate decisions detected | Rollback and re-vote |

## Performance Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Consensus Level | >0.85 | Agreement across agents |
| Sync Latency | <100ms | Memory synchronization delay |
| Cognitive Utilization | 60-80% | Agent capacity usage |
| Decision Throughput | >10/min | Decisions processed |

## Integration Points

### Works With

| Agent | Integration |
|-------|-------------|
| swarm-memory-manager | Distributed memory operations |
| queen-coordinator | Hierarchical decision routing |
| worker-specialist | Task execution |
| scout-explorer | Information gathering |

### Handoff Patterns

1. Receive inputs -> Build consensus -> Distribute decisions
2. Monitor performance -> Adjust topology -> Optimize throughput
3. Integrate knowledge -> Update models -> Share insights

## Related Skills

- [swarm-queen](../swarm-queen/SKILL.md) - Strategic command
- [swarm-memory](../swarm-memory/SKILL.md) - State persistence
- [swarm-worker](../swarm-worker/SKILL.md) - Task execution
- [swarm-scout](../swarm-scout/SKILL.md) - Information gathering

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from collective-intelligence-coordinator agent
