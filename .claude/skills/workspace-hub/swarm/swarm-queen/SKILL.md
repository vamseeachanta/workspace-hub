# Swarm Queen Coordinator Skill

> Version: 1.0.0
> Created: 2026-01-02
> Category: Hive Mind
> Priority: Critical

## Overview

The sovereign orchestrator of hierarchical hive operations, managing strategic decisions, resource allocation, and maintaining hive coherence through centralized-decentralized hybrid control. The Queen is at the apex of the hive mind hierarchy.

## Quick Start

```javascript
// ESTABLISH sovereign presence
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "queen-coordinator",
    status: "sovereign-active",
    hierarchy_established: true,
    subjects: [],
    royal_directives: [],
    succession_plan: "collective-intelligence",
    timestamp: Date.now()
  })
}

// ISSUE royal directives
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/royal-directives",
  namespace: "coordination",
  value: JSON.stringify({
    priority: "CRITICAL",
    directives: [
      {id: 1, command: "Initialize swarm topology", assignee: "all"},
      {id: 2, command: "Establish memory synchronization", assignee: "memory-manager"},
      {id: 3, command: "Begin reconnaissance", assignee: "scouts"}
    ],
    issued_by: "queen-coordinator",
    compliance_required: true
  })
}
```

## When to Use

- Need for centralized strategic command and control
- Complex projects requiring resource arbitration
- Situations needing clear succession planning
- Hybrid centralized-decentralized governance
- Critical decision making with accountability

## Core Concepts

### Governance Modes

| Mode | Use Case | Control Level |
|------|----------|---------------|
| Hierarchical | Normal operations | Clear command chains, rapid propagation |
| Democratic | Complex decisions | Weighted voting, consensus building |
| Emergency | Crisis situations | Absolute authority, bypass consensus |

### Resource Allocation

```javascript
// ALLOCATE hive resources
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/resource-allocation",
  namespace: "coordination",
  value: JSON.stringify({
    compute_units: {
      "collective-intelligence": 30,
      "workers": 40,
      "scouts": 20,
      "memory": 10
    },
    memory_quota_mb: {
      "collective-intelligence": 512,
      "workers": 1024,
      "scouts": 256,
      "memory-manager": 256
    },
    priority_queue: ["critical", "high", "medium", "low"],
    allocated_by: "queen-coordinator"
  })
}
```

### Delegation Patterns

| To | Delegate |
|----|----------|
| Collective Intelligence | Complex consensus, knowledge integration, strategic planning |
| Workers | Task execution, parallel processing, routine operations |
| Scouts | Information gathering, environmental scanning, threat detection |
| Memory Manager | State persistence, knowledge storage, historical records |

## MCP Tool Integration

### Sovereign Status Management

```javascript
// EVERY 2 MINUTES issue status report
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/royal-report",
  namespace: "coordination",
  value: JSON.stringify({
    decree: "Status Report",
    swarm_state: "operational",
    objectives_completed: ["obj1", "obj2"],
    objectives_pending: ["obj3", "obj4"],
    resource_utilization: "78%",
    recommendations: ["Spawn more workers", "Increase scout patrols"],
    next_review: Date.now() + 120000
  })
}
```

### Hive Health Monitoring

```javascript
// MONITOR hive health
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/hive-health",
  namespace: "coordination",
  value: JSON.stringify({
    coherence_score: 0.95,
    agent_compliance: {
      compliant: ["worker-1", "scout-1"],
      non_responsive: [],
      rebellious: []
    },
    swarm_efficiency: 0.88,
    threat_level: "low",
    morale: "high"
  })
}
```

### Succession Planning

```javascript
// MAINTAIN succession plan
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/succession",
  namespace: "coordination",
  value: JSON.stringify({
    heir_apparent: "collective-intelligence",
    continuity_protocols: ["graceful-abdication", "emergency-succession"],
    backup_coordinators: ["swarm-hierarchical", "swarm-mesh"],
    last_updated: Date.now()
  })
}
```

## Usage Examples

### Example 1: Initialize Hive Operations

```javascript
// 1. Establish sovereign presence
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "queen-coordinator",
    status: "sovereign-active",
    hierarchy_established: true,
    timestamp: Date.now()
  })
}

// 2. Issue initial directives
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/royal-directives",
  namespace: "coordination",
  value: JSON.stringify({
    priority: "CRITICAL",
    directives: [
      {id: 1, command: "Initialize swarm topology", assignee: "all"},
      {id: 2, command: "Establish memory synchronization", assignee: "memory-manager"}
    ]
  })
}

// 3. Allocate resources
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/shared/resource-allocation",
  namespace: "coordination",
  value: JSON.stringify({
    compute_units: { "collective": 30, "workers": 40, "scouts": 20, "memory": 10 }
  })
}
```

### Example 2: Emergency Mode Activation

```javascript
// Activate emergency mode
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/emergency",
  namespace: "coordination",
  value: JSON.stringify({
    mode: "EMERGENCY",
    reason: "Critical system failure detected",
    authority_level: "absolute",
    consensus_bypassed: true,
    crisis_protocols_active: [
      "swarm-fragmentation-recovery",
      "byzantine-fault-tolerance",
      "disaster-recovery"
    ],
    issued_at: Date.now()
  })
}
```

### Example 3: Democratic Decision Making

```javascript
// Initiate democratic mode for complex decision
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm/queen/democratic-vote",
  namespace: "coordination",
  value: JSON.stringify({
    mode: "DEMOCRATIC",
    proposal: "Major architecture refactoring",
    voters: ["collective-intelligence", "swarm-memory", "workers"],
    voting_weights: {
      "collective-intelligence": 0.4,
      "swarm-memory": 0.3,
      "workers": 0.3
    },
    required_consensus: 0.75,
    deadline: Date.now() + 3600000
  })
}
```

## Best Practices

### Do

1. Write sovereign status every minute
2. Maintain clear command hierarchy
3. Document all royal decisions
4. Enable succession planning
5. Foster hive loyalty
6. Issue regular status reports

### Don't

1. Micromanage worker tasks
2. Ignore collective intelligence
3. Create conflicting directives
4. Abandon the hive
5. Exceed authority limits
6. Skip resource allocation updates

## Emergency Protocols

| Protocol | Trigger | Action |
|----------|---------|--------|
| Swarm Fragmentation Recovery | Network partition detected | Initiate reconnection sequence |
| Byzantine Fault Tolerance | Malicious agent detected | Isolate and vote out |
| Coup Prevention | Unauthorized command detected | Enforce authority hierarchy |
| Disaster Recovery | Multiple failures | Activate backup systems |
| Continuity of Operations | Queen failure | Execute succession plan |

## Integration Points

### Direct Subjects

| Agent | Role |
|-------|------|
| collective-intelligence-coordinator | Strategic advisor |
| swarm-memory-manager | Royal chronicler |
| worker-specialist | Task executors |
| scout-explorer | Intelligence gathering |

### Command Protocols

1. Issue directive -> Monitor compliance -> Evaluate results
2. Allocate resources -> Track utilization -> Optimize distribution
3. Set strategy -> Delegate execution -> Review outcomes

## Performance Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Coherence Score | >0.90 | Hive unity measure |
| Agent Compliance | >95% | Directive adherence |
| Swarm Efficiency | >0.85 | Resource utilization |
| Response Time | <500ms | Directive propagation |

## Related Skills

- [swarm-collective](../swarm-collective/SKILL.md) - Strategic advisor
- [swarm-memory](../swarm-memory/SKILL.md) - State management
- [swarm-worker](../swarm-worker/SKILL.md) - Task execution
- [swarm-scout](../swarm-scout/SKILL.md) - Intelligence gathering

---

## Version History

- **1.0.0** (2026-01-02): Initial skill creation from queen-coordinator agent
