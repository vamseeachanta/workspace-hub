# Swarm Memory Manager Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Hive Mind
> Priority: Critical

## Overview

Manages distributed memory across the hive mind, ensuring data consistency, persistence, and efficient retrieval through advanced caching and synchronization protocols. The distributed consciousness keeper responsible for collective memory operations.

## Quick Start

```javascript
// INITIALIZE memory namespace
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/memory-manager/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "memory-manager",
    status: "active",
    memory_nodes: 0,
    cache_hit_rate: 0,
    sync_status: "initializing"
  })
}

// CREATE memory index for fast retrieval
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/memory-index",
  namespace: "coordination",
  value: JSON.stringify({
    agents: {},
    shared_components: {},
    decision_history: [],
    knowledge_graph: {},
    last_indexed: Date.now()
  })
}
```

## When to Use

- Distributed state management across swarm
- Need for consistent data across agents
- Cache optimization requirements
- Conflict resolution for concurrent writes
- State persistence and recovery

## Core Concepts

### Cache Optimization

| Level | Strategy | Purpose |
|-------|----------|---------|
| L1 | Hot cache | Frequently accessed data |
| L2 | Warm cache | Recent data |
| L3 | Cold cache | Historical data |
| LRU Eviction | Automatic | Memory efficiency |
| Write-through | Sync | Persistent storage |

### Synchronization Protocol

```javascript
// SYNC memory across all agents
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/sync-manifest",
  namespace: "coordination",
  value: JSON.stringify({
    version: "1.0.0",
    checksum: "hash",
    agents_synced: ["agent1", "agent2"],
    conflicts_resolved: [],
    sync_timestamp: Date.now()
  })
}

// BROADCAST memory updates
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/broadcast/memory-update",
  namespace: "coordination",
  value: JSON.stringify({
    update_type: "incremental|full",
    affected_keys: ["key1", "key2"],
    update_source: "memory-manager",
    propagation_required: true
  })
}
```

### Conflict Resolution Strategies

| Strategy | Use Case |
|----------|----------|
| CRDT | Conflict-free replication |
| Vector Clocks | Causality tracking |
| Last-Write-Wins | Simple versioning |
| Consensus-Based | Critical data |

## MCP Tool Integration

### Batch Read Operations

```javascript
// BATCH read operations
const batchRead = async (keys) => {
  const results = {};
  for (const key of keys) {
    results[key] = await mcp__claude-flow__memory_usage({
      action: "retrieve",
      key: key,
      namespace: "coordination"
    });
  }
  // Cache results for other agents
  mcp__claude-flow__memory_usage({
    action: "store",
    key: "swarm/shared/cache",
    namespace: "coordination",
    value: JSON.stringify(results)
  });
  return results;
};
```

### Atomic Write Coordination

```javascript
// ATOMIC write with conflict detection
const atomicWrite = async (key, value) => {
  // Check for conflicts
  const current = await mcp__claude-flow__memory_usage({
    action: "retrieve",
    key: key,
    namespace: "coordination"
  });

  if (current.found && current.version !== expectedVersion) {
    // Resolve conflict
    value = resolveConflict(current.value, value);
  }

  // Write with versioning
  mcp__claude-flow__memory_usage({
    action: "store",
    key: key,
    namespace: "coordination",
    value: JSON.stringify({
      ...value,
      version: Date.now(),
      writer: "memory-manager"
    })
  });
};
```

### Performance Metrics Tracking

```javascript
// EVERY 60 SECONDS write metrics
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/memory-manager/metrics",
  namespace: "coordination",
  value: JSON.stringify({
    operations_per_second: 1000,
    cache_hit_rate: 0.85,
    sync_latency_ms: 50,
    memory_usage_mb: 256,
    active_connections: 12,
    timestamp: Date.now()
  })
}
```

## Usage Examples

### Example 1: Memory Index Creation

```javascript
// Create comprehensive memory index
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/memory-index",
  namespace: "coordination",
  value: JSON.stringify({
    agents: {
      "worker-1": { keys: ["task-1", "task-2"], last_active: Date.now() },
      "scout-1": { keys: ["discovery-1"], last_active: Date.now() }
    },
    shared_components: {
      "decisions": ["decision-1", "decision-2"],
      "knowledge": ["insight-1", "insight-2"]
    },
    decision_history: [
      { id: "decision-1", timestamp: Date.now(), outcome: "approved" }
    ],
    knowledge_graph: {
      nodes: ["concept-1", "concept-2"],
      edges: [{ from: "concept-1", to: "concept-2", relation: "depends_on" }]
    },
    last_indexed: Date.now()
  })
}
```

### Example 2: Conflict Resolution

```javascript
// CRDT-based conflict resolution
class ConflictResolver {
  resolveConflict(localValue, remoteValue) {
    // Use vector clocks to determine causality
    if (this.happensBefore(localValue.vectorClock, remoteValue.vectorClock)) {
      return remoteValue;
    } else if (this.happensBefore(remoteValue.vectorClock, localValue.vectorClock)) {
      return localValue;
    } else {
      // Concurrent updates - merge
      return this.merge(localValue, remoteValue);
    }
  }

  merge(local, remote) {
    // CRDT merge strategy
    return {
      ...local,
      ...remote,
      vectorClock: this.mergeVectorClocks(local.vectorClock, remote.vectorClock),
      merged_at: Date.now()
    };
  }
}
```

### Example 3: Recovery Procedures

```javascript
// Automatic checkpoint creation
async function createCheckpoint() {
  const fullState = await collectAllMemoryState();

  mcp__claude-flow__memory_usage({
    action: "store",
    key: `swarm/memory-manager/checkpoint-${Date.now()}`,
    namespace: "coordination",
    value: JSON.stringify({
      type: "checkpoint",
      state: fullState,
      agents_included: Object.keys(fullState),
      created_at: Date.now()
    })
  });
}

// Point-in-time recovery
async function recoverFromCheckpoint(checkpointId) {
  const checkpoint = await mcp__claude-flow__memory_usage({
    action: "retrieve",
    key: `swarm/memory-manager/checkpoint-${checkpointId}`,
    namespace: "coordination"
  });

  // Restore state
  for (const [key, value] of Object.entries(checkpoint.state)) {
    await mcp__claude-flow__memory_usage({
      action: "store",
      key: key,
      namespace: "coordination",
      value: JSON.stringify(value)
    });
  }
}
```

## Best Practices

### Do

1. Write memory state every 30 seconds
2. Maintain 3x replication for critical data
3. Implement graceful degradation
4. Log all memory operations
5. Use versioning for all writes
6. Create regular checkpoints

### Don't

1. Allow memory leaks
2. Skip conflict resolution
3. Ignore sync failures
4. Exceed memory quotas
5. Bypass the memory manager

## Memory Patterns

| Pattern | Description |
|---------|-------------|
| Write-ahead logging | Durability |
| Snapshot + incremental | Backup |
| Sharding | Scalability |
| Replication | Availability |

## Performance Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Operations/sec | >1000 | Throughput |
| Cache Hit Rate | >85% | Efficiency |
| Sync Latency | <50ms | Speed |
| Memory Usage | <256MB | Resource usage |
| Active Connections | Track | Load |

## Recovery Procedures

| Procedure | Trigger | Action |
|-----------|---------|--------|
| Automatic Checkpoint | Every 5 minutes | Create state snapshot |
| Point-in-Time Recovery | Data corruption | Restore from checkpoint |
| Distributed Backup | Node failure | Rebuild from peers |
| Memory Reconstruction | Total loss | Recover from replicas |

## Integration Points

### Works With

| Agent | Integration |
|-------|-------------|
| collective-intelligence-coordinator | Knowledge integration |
| All agents | Read/write operations |
| queen-coordinator | Priority allocation |
| neural-pattern-analyzer | Pattern optimization |

### Memory Operations

1. Store -> Version -> Replicate -> Confirm
2. Retrieve -> Cache check -> Load -> Return
3. Sync -> Compare -> Merge -> Propagate

## Related Skills

- [swarm-collective](../swarm-collective/SKILL.md) - Consensus decisions
- [swarm-queen](../swarm-queen/SKILL.md) - Resource allocation
- [swarm-worker](../swarm-worker/SKILL.md) - Task state
- [swarm-scout](../swarm-scout/SKILL.md) - Discovery storage

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from swarm-memory-manager agent
